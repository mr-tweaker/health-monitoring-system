const API_URL = "http://192.168.1.10:8000/integrations/zepp/ingest"; // replace if LAN IP changes

async function pushVitals(v) {
  const body = {
    patient_id: "PAT001",
    timestamp: Math.floor(Date.now() / 1000),
    heart_rate: v.hr,
    spo2: v.spo2,
    temperature: v.temp,
    blood_pressure_systolic: v.bpSys,
    blood_pressure_diastolic: v.bpDia,
    device_id: "amazfit_band_7"
  };
  try {
    await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body)
    });
  } catch (e) {}
}

// TODO: wire real values via ZML/BLE from the Device App
setInterval(() => pushVitals({ hr: 80, spo2: 97 }), 60000);
