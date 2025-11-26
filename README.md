# 🚨 Guardian — AI-Powered FIR Crime Mapping System

Guardian is an end-to-end crime processing, geocoding, and visualization system that extracts information from FIR PDFs, stores them in a Supabase database, converts location text into latitude/longitude using MapMyIndia Geocoding API, and finally plots all crime points on an interactive map using Mappls Maps.

# ✨ Features
🔍 1. Automated FIR Extraction
- Reads FIR PDF files
- Extracts key details using AI (LangChain+Gemini)
- Stores structured results into Supabase
- Handles complainant, accused, sections, summary, etc.

🗺️ 2. Intelligent Geocoding
- Converts FIR location text → Latitude/Longitude
- MapMyIndia Geocoding API
- Urban bias + Sublocality filter for accuracy
- Automatic retries + error handling
- Stores coordinates back into Supabase

📌 3. Interactive Crime Map (Frontend)
- Plots each FIR on Mappls Maps
- Custom markers
- Popup box shows:
- Crime Category
- Incident Summary
- Scrollable popup for long content
- Clean UI

⚙️ 4. FastAPI Backend
- /api/fir-data endpoint returns all FIR geocoded entries
- Clean SQLAlchemy ORM-based CRUD
- Connected directly to Supabase PostgreSQL

# 🔧 Installation & Setup
1️⃣ Clone the Repository
```bash
git clone https://github.com/Swayam8115/guardian.git
cd guardian
```
2️⃣ 🐍 Install Dependencies
```bash
pip install -r requirements.txt
```

- If you don’t have FastAPI / Uvicorn installed:
```bash
pip install fastapi uvicorn sqlalchemy requests python-dotenv
```
3️⃣ ⚙️ Environment Variables

Create .env in the project root:
```bash
GOOGLE_API_KEY=your_gemini_api_key_here
SUPABASE_DB_URL=postgresql+psycopg2://..
MAPMYINDIA_API_KEY=xxxxxxxx
MAPMYINDIA_SECRET=xxxxxxxx
DATA_PATH=data/
OUTPUT_PATH=output/
PROMPTS_PATH=prompts/
```
4️⃣ 🧠 Run FIR Processing 
- Processes all FIR PDFs and inserts into Supabase:
```bash
python main.py
```

This runs:
- process_all_firs() → Extract FIR data
- run_geo_code() → Geocode missing coordinates

5️⃣ 🚀 Start Backend Server

Run FastAPI Server:
```bash
uvicorn backend.server_main:app --reload --port 8000
```
- Backend API now available at: http://127.0.0.1:8000/api/fir-data

6️⃣ 🌍 Run Frontend Map

- Go to frontend folder:
```bash
cd frontend/map
```

Start a static server:
```bash
python -m http.server 5500
```

- Open in browser: http://127.0.0.1:5500/index.html

You will now see every FIR plotted on the map

# 🛠️ Technologies Used
- Python
- LangChain + Gemini
- Supabase PostgreSQL
- SQLAlchemy ORM
- FastAPI
- MapMyIndia / Mappls Maps
- HTML + JS Frontend