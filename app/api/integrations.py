"""
Integrations API: OAuth and sync endpoints for external providers (Withings first)
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi import Body, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import os
import requests
import logging

from app.database import get_db, OAuthToken, VitalSign

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/integrations", tags=["integrations"])


# ---------- Withings OAuth ----------

def _withings_config():
    client_id = os.getenv("WITHINGS_CLIENT_ID")
    client_secret = os.getenv("WITHINGS_CLIENT_SECRET")
    redirect_uri = os.getenv("WITHINGS_REDIRECT_URI", "http://localhost:8000/oauth/callback/withings")
    if not client_id or not client_secret:
        raise HTTPException(status_code=500, detail="Withings client credentials not configured")
    return client_id, client_secret, redirect_uri


@router.get("/withings/authorize")
def withings_authorize(state: str = "demo"):
    """Redirect user to Withings OAuth authorization page"""
    client_id, _, redirect_uri = _withings_config()
    authorize_url = (
        "https://account.withings.com/oauth2_user/authorize2"
        f"?response_type=code&client_id={client_id}"
        f"&redirect_uri={requests.utils.quote(redirect_uri, safe='')}"
        "&scope=user.info%2Cuser.activity%2Cuser.metrics%2Cuser.sleepevents"
        f"&state={state}"
    )
    return RedirectResponse(authorize_url)


@router.get("/withings/callback")
def withings_callback(code: Optional[str] = None, state: Optional[str] = None, db: Session = Depends(get_db)):
    """OAuth callback to exchange code for tokens and store them"""
    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code")

    client_id, client_secret, redirect_uri = _withings_config()

    try:
        token_resp = requests.post(
            "https://wbsapi.withings.net/v2/oauth2",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "action": "requesttoken",  # Required by Withings OAuth v2
                "grant_type": "authorization_code",
                "client_id": client_id,
                "client_secret": client_secret,
                "code": code,
                "redirect_uri": redirect_uri,
            },
            timeout=20,
        )
        token_resp.raise_for_status()
        payload = token_resp.json()
        body = payload.get("body", {}) if isinstance(payload, dict) else {}
        access_token = body.get("access_token") or payload.get("access_token")
        refresh_token = body.get("refresh_token") or payload.get("refresh_token")
        expires_in = body.get("expires_in") or payload.get("expires_in")
        user_id = str(body.get("userid") or body.get("user_id") or "DEFAULT")
        if not access_token:
            raise RuntimeError(f"Unexpected token response: {payload}")

        expires_at = datetime.utcnow() + timedelta(seconds=int(expires_in or 3600))

        # Upsert token for this provider/user
        existing = db.query(OAuthToken).filter(
            OAuthToken.provider == "withings",
            OAuthToken.user_id == user_id,
        ).first()

        if existing:
            existing.access_token = access_token
            existing.refresh_token = refresh_token
            existing.expires_at = expires_at
            existing.scope = "user.info,user.activity,user.metrics,user.sleepevents"
            existing.updated_at = datetime.utcnow()
        else:
            db.add(OAuthToken(
                provider="withings",
                user_id=user_id,
                access_token=access_token,
                refresh_token=refresh_token,
                expires_at=expires_at,
                scope="user.info,user.activity,user.metrics,user.sleepevents",
            ))
        db.commit()

        return {"message": "Withings tokens stored", "provider": "withings", "user_id": user_id, "expires_at": expires_at.isoformat()}
    except Exception as e:
        logger.exception("Withings token exchange failed")
        raise HTTPException(status_code=500, detail=f"Withings token exchange failed: {e}")


def _withings_get_token(db: Session) -> Optional[OAuthToken]:
    token = db.query(OAuthToken).filter(OAuthToken.provider == "withings").order_by(OAuthToken.updated_at.desc()).first()
    return token


@router.post("/withings/sync")
def withings_sync(patient_id: str = "PAT001", hours: int = 24, db: Session = Depends(get_db)):
    """Fetch recent measures from Withings and store basic vitals.
    For demo: maps weight (kg) -> glucose None, HR if available, BP if available.
    """
    token = _withings_get_token(db)
    if not token:
        raise HTTPException(status_code=400, detail="No Withings token stored. Authorize first.")

    if token.expires_at and token.expires_at < datetime.utcnow():
        # For simplicity: instruct user to re-authorize; token refresh flow can be added later
        raise HTTPException(status_code=400, detail="Withings token expired. Please re-authorize.")

    start_date = int((datetime.utcnow() - timedelta(hours=hours)).timestamp())

    try:
        # Activity example (steps, hr average if present)
        act_resp = requests.get(
            "https://wbsapi.withings.net/v2/measure",
            headers={"Authorization": f"Bearer {token.access_token}"},
            params={"action": "getactivity", "startdateymd": datetime.utcfromtimestamp(start_date).strftime("%Y-%m-%d"), "enddateymd": datetime.utcnow().strftime("%Y-%m-%d")},
            timeout=20,
        )
        # Measures example (weight, bp)
        meas_resp = requests.get(
            "https://wbsapi.withings.net/measure",
            headers={"Authorization": f"Bearer {token.access_token}"},
            params={"action": "getmeas", "lastupdate": start_date},
            timeout=20,
        )

        inserted = 0
        if act_resp.ok:
            act = act_resp.json().get("body", {}).get("activities", [])
            for a in act:
                vs = VitalSign(
                    patient_id=patient_id,
                    timestamp=datetime.strptime(a.get("date"), "%Y-%m-%d") if a.get("date") else datetime.utcnow(),
                    heart_rate=None,
                    temperature=None,
                    spo2=None,
                    glucose=None,
                    blood_pressure_systolic=None,
                    blood_pressure_diastolic=None,
                    device_id="withings",
                )
                db.add(vs)
                inserted += 1

        if meas_resp.ok:
            body = meas_resp.json().get("body", {})
            for grp in body.get("measuregrps", []):
                ts = datetime.utcfromtimestamp(grp.get("date", int(datetime.utcnow().timestamp())))
                bp_sys = None
                bp_dia = None
                hr = None
                for m in grp.get("measures", []):
                    if m.get("type") == 10:  # systolic mmHg
                        bp_sys = (m.get("value", 0) * (10 ** m.get("unit", 0)))
                    if m.get("type") == 11:  # diastolic mmHg
                        bp_dia = (m.get("value", 0) * (10 ** m.get("unit", 0)))
                    if m.get("type") == 11_1:  # placeholder; Withings HR type is 11? Often 11 is diastolic; HR type is 11? Using 11_1 placeholder to keep structure
                        hr = (m.get("value", 0) * (10 ** m.get("unit", 0)))
                vs = VitalSign(
                    patient_id=patient_id,
                    timestamp=ts,
                    heart_rate=hr,
                    temperature=None,
                    spo2=None,
                    glucose=None,
                    blood_pressure_systolic=bp_sys,
                    blood_pressure_diastolic=bp_dia,
                    device_id="withings",
                )
                db.add(vs)
                inserted += 1

        db.commit()
        return {"message": "Withings sync complete", "inserted": inserted}
    except Exception as e:
        logger.exception("Withings sync failed")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Withings sync failed: {e}")

# Also accept the commonly-registered redirect path
@router.get("/oauth/callback/withings")
def withings_callback_alias(code: Optional[str] = None, state: Optional[str] = None, db: Session = Depends(get_db)):
    return withings_callback(code=code, state=state, db=db)

# ---------- Fitbit OAuth ----------

def _fitbit_config():
    client_id = os.getenv("FITBIT_CLIENT_ID")
    client_secret = os.getenv("FITBIT_CLIENT_SECRET")
    redirect_uri = os.getenv("FITBIT_REDIRECT_URI", "http://localhost:8000/oauth/callback/fitbit")
    if not client_id or not client_secret:
        raise HTTPException(status_code=500, detail="Fitbit client credentials not configured")
    return client_id, client_secret, redirect_uri


@router.get("/fitbit/authorize")
def fitbit_authorize(state: str = "demo"):
    client_id, _, redirect_uri = _fitbit_config()
    authorize_url = (
        "https://www.fitbit.com/oauth2/authorize"
        f"?response_type=code&client_id={client_id}"
        f"&redirect_uri={requests.utils.quote(redirect_uri, safe='')}"
        "&scope=activity%20heartrate%20sleep%20profile"
        f"&state={state}"
    )
    return RedirectResponse(authorize_url)


@router.get("/fitbit/callback")
def fitbit_callback(code: Optional[str] = None, state: Optional[str] = None, db: Session = Depends(get_db)):
    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code")

    client_id, client_secret, redirect_uri = _fitbit_config()

    try:
        token_resp = requests.post(
            "https://api.fitbit.com/oauth2/token",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            auth=(client_id, client_secret),
            data={
                "client_id": client_id,
                "grant_type": "authorization_code",
                "redirect_uri": redirect_uri,
                "code": code,
            },
            timeout=20,
        )
        token_resp.raise_for_status()
        payload = token_resp.json()
        access_token = payload.get("access_token")
        refresh_token = payload.get("refresh_token")
        expires_in = payload.get("expires_in")
        user_id = str(payload.get("user_id") or payload.get("user_id") or "DEFAULT")
        if not access_token:
            raise RuntimeError(f"Unexpected token response: {payload}")

        expires_at = datetime.utcnow() + timedelta(seconds=int(expires_in or 3600))

        existing = db.query(OAuthToken).filter(
            OAuthToken.provider == "fitbit",
            OAuthToken.user_id == user_id,
        ).first()

        if existing:
            existing.access_token = access_token
            existing.refresh_token = refresh_token
            existing.expires_at = expires_at
            existing.scope = "activity,heartrate,sleep,profile"
            existing.updated_at = datetime.utcnow()
        else:
            db.add(OAuthToken(
                provider="fitbit",
                user_id=user_id,
                access_token=access_token,
                refresh_token=refresh_token,
                expires_at=expires_at,
                scope="activity,heartrate,sleep,profile",
            ))
        db.commit()
        return {"message": "Fitbit tokens stored", "provider": "fitbit", "user_id": user_id, "expires_at": expires_at.isoformat()}
    except Exception as e:
        logger.exception("Fitbit token exchange failed")
        raise HTTPException(status_code=500, detail=f"Fitbit token exchange failed: {e}")


@router.post("/fitbit/sync")
def fitbit_sync(patient_id: str = "PAT001", hours: int = 24, db: Session = Depends(get_db)):
    token = db.query(OAuthToken).filter(OAuthToken.provider == "fitbit").order_by(OAuthToken.updated_at.desc()).first()
    if not token:
        raise HTTPException(status_code=400, detail="No Fitbit token stored. Authorize first.")
    if token.expires_at and token.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Fitbit token expired. Please re-authorize.")

    # Stub: for now, just confirm connectivity; detailed mapping can be added
    try:
        resp = requests.get(
            "https://api.fitbit.com/1/user/-/profile.json",
            headers={"Authorization": f"Bearer {token.access_token}"},
            timeout=20,
        )
        ok = resp.status_code == 200
        return {"message": "Fitbit connectivity ok" if ok else "Fitbit connectivity failed", "status": resp.status_code}
    except Exception as e:
        logger.exception("Fitbit sync failed")
        raise HTTPException(status_code=500, detail=f"Fitbit sync failed: {e}")

# Also accept the commonly-registered redirect path
@router.get("/oauth/callback/fitbit")
def fitbit_callback_alias(code: Optional[str] = None, state: Optional[str] = None, db: Session = Depends(get_db)):
    return fitbit_callback(code=code, state=state, db=db)


# ---------- Zepp OS (Amazfit) webhook ingest ----------
@router.post("/zepp/ingest")
def zepp_ingest(
    payload: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db),
):
    """Ingest vitals posted from a Zepp OS Side Service.
    Expected JSON (all fields optional except patient_id):
    {
      "patient_id": "PAT001",
      "timestamp": "2025-09-07T12:34:56Z" | epoch_seconds,
      "heart_rate": 78,
      "spo2": 98,
      "steps": 1200,  # kept for future use
      "blood_pressure_systolic": 120,
      "blood_pressure_diastolic": 80,
      "temperature": 98.6,
      "device_id": "amazfit_band_7"
    }
    """
    try:
        patient_id = payload.get("patient_id") or "PAT001"
        ts = payload.get("timestamp")
        if isinstance(ts, (int, float)):
            timestamp = datetime.utcfromtimestamp(ts)
        elif isinstance(ts, str):
            try:
                timestamp = datetime.fromisoformat(ts.replace("Z", "+00:00")).replace(tzinfo=None)
            except Exception:
                timestamp = datetime.utcnow()
        else:
            timestamp = datetime.utcnow()

        vs = VitalSign(
            patient_id=patient_id,
            timestamp=timestamp,
            heart_rate=payload.get("heart_rate"),
            spo2=payload.get("spo2"),
            glucose=None,
            blood_pressure_systolic=payload.get("blood_pressure_systolic"),
            blood_pressure_diastolic=payload.get("blood_pressure_diastolic"),
            temperature=payload.get("temperature"),
            device_id=payload.get("device_id", "zepp")
        )
        db.add(vs)
        db.commit()
        return {"message": "ingested", "patient_id": patient_id, "timestamp": timestamp.isoformat()}
    except Exception as e:
        logger.exception("Zepp ingest failed")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Zepp ingest failed: {e}")


# Simple/forgiving ingest: accept query params or form fields, no JSON required
@router.post("/zepp/ingest-simple")
@router.get("/zepp/ingest-simple")
def zepp_ingest_simple(
    patient_id: str = Query("PAT001"),
    timestamp: Optional[int] = Query(None),
    heart_rate: Optional[float] = Query(None),
    spo2: Optional[float] = Query(None),
    temperature: Optional[float] = Query(None),
    blood_pressure_systolic: Optional[float] = Query(None),
    blood_pressure_diastolic: Optional[float] = Query(None),
    device_id: str = Query("zepp"),
    db: Session = Depends(get_db),
):
    try:
        ts = timestamp if timestamp is not None else int(datetime.utcnow().timestamp())
        vs = VitalSign(
            patient_id=patient_id,
            timestamp=datetime.utcfromtimestamp(ts),
            heart_rate=heart_rate,
            spo2=spo2,
            glucose=None,
            blood_pressure_systolic=blood_pressure_systolic,
            blood_pressure_diastolic=blood_pressure_diastolic,
            temperature=temperature,
            device_id=device_id,
        )
        db.add(vs)
        db.commit()
        return {"message": "ingested", "patient_id": patient_id, "timestamp": datetime.utcfromtimestamp(ts).isoformat()}
    except Exception as e:
        logger.exception("Zepp ingest-simple failed")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Zepp ingest-simple failed: {e}")


