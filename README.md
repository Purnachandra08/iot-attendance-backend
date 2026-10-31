# IoT Attendance Backend — Supabase Cloud Edition

Migrated from the uploaded SQLite Express backend. React API response shapes and routes are preserved. Supabase PostgreSQL stores student, device and attendance records; a **private Supabase Storage bucket** stores student enrollment images and ESP32-CAM captures. Camera endpoint accepts JPEG uploads from ESP32-CAM. Optional Python recognition service can identify a face and mark attendance; without it camera upload succeeds but attendance is NOT marked.

## 1. Create cloud database (free-tier possible)

1. Create a Supabase project at https://supabase.com/dashboard.
2. In **SQL Editor**, paste/run the complete `schema.sql` file. This creates tables, 3 example devices, and private `face-images` bucket.
3. Under **Project Settings > API** (or API Keys), copy your Project URL and **service_role** key (or secret API key compatible with `supabase-js`). The service-role key is **SERVER ONLY**. Never put it in Arduino or React/Vite or commit it to GitHub.
4. Copy `.env.example` to `.env` and enter the URL, secret key, JWT_SECRET, DEVICE_KEY and ADMIN_PASSWORD. Keep `.env` private. `CORS_ORIGIN` is the frontend URL; multiple origins may be comma-separated.

## 2. Install and start (Windows PowerShell / VS Code terminal)

```powershell
cd attendance-backend
npm install
npm run create-admin
npm run dev
```

Visit `http://localhost:5000/api/health` — expected `database: connected`. Sign in on the React frontend with ADMIN_USERNAME / ADMIN_PASSWORD from `.env`.

The original SQLite DB and face uploads were deliberately **not included** in this ZIP to avoid distributing student images, database contents and secrets. Old data is not migrated automatically; re-register students in the React dashboard or export/import after verifying permission. Seed example devices are `ROBOT_01`, `ROBOT_02`, `ROBOT_03`.

## 3. Test camera endpoint from laptop before ESP32

Create a JPEG image `test.jpg` in the backend directory, then use Windows PowerShell:

```powershell
curl.exe -X POST "http://localhost:5000/api/devices/ROBOT_01/recognize" -H "Content-Type: image/jpeg" -H "x-device-key: YOUR_DEVICE_KEY" --data-binary "@test.jpg"
```

Expected JSON includes `received:true`, `recognized:false`, `attendanceMarked:false` if optional recognition service is not running. Check Supabase Dashboard > Storage > face-images > captures. This proves image upload and cloud storage work.

## 4. ESP32-CAM hotspot configuration

Connect laptop and ESP32-CAM to same **2.4 GHz hotspot**. On laptop run `ipconfig` and find Wi-Fi IPv4 (example `192.168.43.105`). Arduino sketch:

```cpp
const char* WIFI_SSID = "YOUR_HOTSPOT_NAME";
const char* WIFI_PASSWORD = "YOUR_HOTSPOT_PASSWORD";
const char* UPLOAD_URL = "http://192.168.43.105:5000/api/devices/ROBOT_01/recognize";
const char* DEVICE_KEY = "SAME_VALUE_AS_BACKEND_ENV";
```

Start backend and keep laptop awake. Allow inbound TCP 5000 on Windows Firewall for trusted/private network. Mobile hotspots sometimes isolate devices. ESP32 HTTP uploads are unencrypted on local Wi-Fi; use only a trusted demo hotspot. For production use HTTPS with certificate validation and per-device authentication.

The sketch must send JPEG bytes as POST with `Content-Type: image/jpeg` and header `x-device-key: <DEVICE_KEY>`; check the sketch has this header. Do not send multipart unless you change this endpoint.

## 5. Optional experimental face recognition (separate Python service)

**Not required for testing the camera.** Face matching is optional and heavier than Node.js; CPU inference can be slow. The provided service uses DeepFace Facenet512, compares each enrolled image and only returns a student ID on verified matches. It is a prototype, not a biometric security system: a single photograph per student and no liveness detection make false matches/spoofing possible. Obtain student consent and comply with school privacy requirements.

Use Python 3.10/3.11 with a virtual environment:

```powershell
cd recognition-service
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:RECOGNITION_KEY="YOUR_SEPARATE_RECOGNITION_KEY"
uvicorn app:app --host 127.0.0.1 --port 8000
```

In backend `.env`:

```
RECOGNITION_URL=http://127.0.0.1:8000
RECOGNITION_KEY=YOUR_SEPARATE_RECOGNITION_KEY
```

Restart backend. Register each student with a clear frontal face photograph via React. Recognition may download model weights on first run (internet required). Test with consent and varied lighting. If Python service fails, Node reports an error instead of falsely marking attendance.

## 6. API routes

- `POST /api/auth/login` admin login
- `GET /api/auth/me`
- `GET/POST /api/students`, `GET/DELETE /api/students/:id`
- `GET/POST /api/attendance`
- `GET/POST /api/devices`, `GET/PATCH /api/devices/:id`
- `POST /api/devices/:id/heartbeat` requires `x-device-key`
- `POST /api/devices/:id/detection` requires `x-device-key`, accepts `{studentId}` (testing only; don't use as biometric proof)
- `POST /api/devices/:id/recognize` requires `x-device-key`, raw JPEG image
- `GET /api/reports/daily?date=YYYY-MM-DD`
- `GET /api/reports/monthly?month=YYYY-MM`
- `GET /api/events` JWT-required SSE (frontend currently polls)

## 7. Hosting

Supabase hosts database and private image storage, **not this Express API**. For now, run Express on laptop to test with ESP32. To work without laptop, deploy Express on a persistent Node hosting service, and deploy Python separately if using recognition. Then change `UPLOAD_URL` to the public HTTPS API address. Vercel frontend deployment alone cannot run your local backend. Keep secret keys in host environment settings, not in React.

## Notes

- New installs need `npm install` because package dependencies changed.
- This starter API uses application-side report aggregation and can fetch at most 5,000 attendance records per listing / 10,000 per monthly report. For large institutions add pagination and SQL aggregate RPCs.
- The Python demo is compute-heavy and can exceed timeout with many enrolled students; cache embeddings and use liveness checks before real deployment.
- Cloud data is live only if your Supabase project is configured and online. No cloud credentials are embedded in the ZIP.
