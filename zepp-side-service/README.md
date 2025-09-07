Zepp OS Side Service (Amazfit) - Quick Start

1) Prereqs
- Install Node.js (LTS)
- Phone and PC on same Wi‑Fi
- API running at http://192.168.1.10:8000 (adjust IP if needed)

2) Files
- app.json (enables side service + fetch)
- side/index.js (posts vitals every 60s to your API)

3) Install deps
```bash
cd zepp-side-service
npm i
```

4) Configure
- Edit `side/index.js` and set `API_URL` to your PC LAN IP if it changes.
- Optional: replace dummy vitals with real values forwarded from Device App via ZML.

5) Build & Run
- Open this folder in Zepp OS Dev Tools / IDE
- Pair the Zepp mobile app (Developer Mode)
- Run/Install the Mini Program; keep the app in background to let the side service run

6) Verify
```bash
curl -s "http://localhost:8000/api/patients/PAT001/vitals?hours=1" | jq '.[0:5]'
```

References
- Zepp OS workshop (Side Service → Web server): https://github.com/orgs/zepp-health/discussions/276
- Example phone-side approach (SleepAgent): https://gitlab.aiursoft.cn/anduin/sleepagent/
