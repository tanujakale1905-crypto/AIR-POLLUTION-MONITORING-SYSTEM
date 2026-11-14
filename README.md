# 🌍 EcoPulse: Air Pollution Monitoring System
**Full-Stack Environmental Intelligence & Pollution Analytics Platform**  
*Academic Internship & Capstone Software Engineering Project*

---

## 📌 1. Project Overview

The **Air Pollution Monitoring System (EcoPulse)** is a comprehensive, production-grade web application developed with **Python (Flask)**, **SQLAlchemy**, and **modern Vanilla JavaScript with Chart.js**. The system delivers real-time-style atmospheric monitoring, continuous pollution alerting, automated classification, and historical trend analysis for key environmental metrics:

- **PM2.5 (Fine Particulate Matter)** (µg/m³)
- **CO2 (Carbon Dioxide Concentration)** (ppm)
- **Ambient Temperature** (°C and °F)
- **Relative Humidity** (%)

> **⚠️ ACADEMIC NOTICE:**  
> This project is a pure software implementation designed for demonstration, evaluation, and educational testing. It uses a **mathematically realistic sensor simulator engine** (incorporating random walk dynamics, diurnal drifts, and rush-hour spike injections) to generate continuous environmental telemetry without requiring physical hardware sensors.

---

## 🛠️ 2. Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Programming Language** | Python 3.10+ (tested on Python 3.15) | Core backend logic, simulations, data processing |
| **Web Framework** | Flask 3.x | Lightweight, robust WSGI web application server & RESTful API |
| **ORM / Database Layer** | Flask-SQLAlchemy 3.x / SQLAlchemy 2.x | High-level Object Relational Mapping |
| **Database** | SQLite 3 (Default) / MySQL 8.0+ | Zero-configuration local database with MySQL interchangeability |
| **Frontend UI** | HTML5, CSS3 (Modern Glassmorphic Dark UI) | Responsive, mobile-friendly interface |
| **Data Visualization** | Chart.js 4.4 | Real-time streaming line charts, dual-axis charts, and status doughnut graphs |
| **API Architecture** | Flask RESTful JSON API | Standardized endpoints for IoT telemetry ingestion and query retrieval |
| **IDE Environment** | Visual Studio Code | Preconfigured debugging profiles in `.vscode/` |

---

## 🚀 3. Key Modules and Main Features

### A. Real-Time Dashboard
- **Live Metric Cards**: Instant display of PM2.5, CO2, Temperature, and Relative Humidity with color-coded status badges and dynamic progress bars.
- **Overall Status Hero Banner**: Automatic evaluation into **Good** (Green), **Moderate** (Amber), or **Poor** (Red) based on the *Maximum Severity Principle*.
- **Continuous Telemetry Stream**: Live updating recent readings table with micro-animations.
- **Last Synchronized Ticker**: Live ticking counter displaying elapsed time since the latest sensor event.

### B. Intelligent Sensor Simulation Engine
- **Daemon Simulator Worker**: A thread-safe background service executing periodic sensor ticks (default: every 3 seconds).
- **Realistic Physical Modeling**: Uses bounded Gaussian random walks, diurnal mean-reverting pull, and rush-hour traffic simulation.
- **Interactive Controls**:
  - `Generate Reading Now`: Triggers an immediate sensor snapshot.
  - `Inject Pollution Spike`: Intentionally generates an elevated event (PM2.5 > 75 µg/m³, CO2 > 1300 ppm) to showcase the alert notification banner and color changes in real time.
  - `Pause / Resume`: Toggles background generator thread safely.

### C. Automated Alert & Warning System
- **Contextual Notifications**: Alerts trigger automatically whenever any pollutant or climatic factor breaches safe guidelines:
  - **PM2.5 > 60 µg/m³**: *CRITICAL: Poor Air Quality (Hazardous fine particulates)*
  - **CO2 > 1200 ppm**: *CRITICAL: Poor Ventilation Alert (High CO2 concentration)*
  - **Temperature < 10°C or > 38°C**: *Thermal Stress Warning*
  - **Humidity < 20% or > 80%**: *Humidity Extremes Warning*
- **Floating Toast Notifications**: Instant pop-up alert notifications on critical events.

### D. Historical Data Management & Explorer
- Full tabular view of all past records stored in database table `air_quality_readings`.
- **Multi-parameter Filtering**: Filter records by Date Range (`start_date`, `end_date`), Air Quality Status (`Good`, `Moderate`, `Poor`), and rows per page.
- **Pagination**: Responsive previous/next controls with dynamic page pills.
- **CSV Data Export**: One-click download of all environmental history as a `.csv` file.
- **Sample Data Seeder**: Instant re-seeding of 40 historical readings across a 24-hour window.

### E. Analytics & Statistical Breakdown
- Aggregated statistical computation: **Minimum**, **Maximum**, and **Average** for PM2.5, CO2, Temperature, and Humidity.
- **Status Distribution Doughnut Chart**: Interactive visual breakdown of Good vs. Moderate vs. Poor reading proportions.
- **Environmental Safety Matrix**: Built-in benchmark table explaining WHO and NAAQS health impact standards.

### F. REST API & Developer Explorer
- Dedicated in-app interactive API documentation (`/api-docs`) with sample request payloads, cURL snippets, and JSON response definitions.

---

## 🗄️ 4. Database Design

The database schema utilizes the table `air_quality_readings`:

```sql
CREATE TABLE air_quality_readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pm25 REAL NOT NULL,
    co2 REAL NOT NULL,
    temperature REAL NOT NULL,
    humidity REAL NOT NULL,
    air_quality_status VARCHAR(20) NOT NULL DEFAULT 'Good',
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_air_readings_timestamp ON air_quality_readings (timestamp);
CREATE INDEX idx_air_readings_status ON air_quality_readings (air_quality_status);
```

### Classification Logic:
$$\text{Status} = \begin{cases} 
\text{Poor} & \text{if } \text{PM2.5} > 60.0 \text{ or } \text{CO}_2 > 1200.0 \\ 
\text{Moderate} & \text{else if } \text{PM2.5} > 30.0 \text{ or } \text{CO}_2 > 800.0 \\ 
\text{Good} & \text{otherwise} 
\end{cases}$$

---

## 📂 5. Project Directory Structure

```text
air-pollution-monitoring-system/
├── app.py                     # Flask application factory & WSGI server entry point
├── config.py                  # Environment configuration, database paths & thresholds
├── models.py                  # SQLAlchemy AirQualityReading model & classification methods
├── routes.py                  # Frontend template routes & REST API endpoints
├── simulator.py               # Simulated sensor generation engine & background daemon
├── requirements.txt           # Python dependency specifications
├── README.md                  # Complete project guide and documentation
├── PROJECT_REPORT.md          # 20-Section Comprehensive Internship Project Report
├── .vscode/
│   ├── launch.json            # VS Code debug and run configurations
│   └── settings.json          # VS Code Python test runner settings
├── database/
│   ├── air_pollution.db       # SQLite local database (generated on first boot)
│   ├── init_db.py             # Standalone database initialization & seed utility
│   └── schema.sql             # Raw DDL SQL schema for SQLite & MySQL
├── templates/
│   ├── base.html              # Master layout (header, nav, toast container, footer)
│   ├── index.html             # Live Real-time Dashboard & Streaming Charts
│   ├── history.html           # Historical Data Explorer with filters & pagination
│   ├── analytics.html         # Statistical analytics & status distribution
│   └── api_docs.html          # Interactive REST API explorer & cURL examples
├── static/
│   ├── css/
│   │   └── style.css          # Modern dark glassmorphic responsive stylesheet
│   └── js/
│       ├── charts.js          # Chart.js initialization & live stream handler
│       ├── dashboard.js       # Live polling, metric card updater, and controls
│       └── history.js         # History table filter, search, and pagination
└── tests/
    └── test_app.py            # Complete unit and integration test suite (12 tests)
```

---

## ⚡ 6. Installation & Setup Instructions

### Step 1: Open the Project in VS Code
Open Visual Studio Code, click **File > Open Folder...**, and select the `air pollution` project folder.

### Step 2: Open an Integrated Terminal
In VS Code, press ``Ctrl + ` `` (or select **Terminal > New Terminal**).

### Step 3: (Recommended) Create and Activate a Virtual Environment
```bash
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### Step 4: Install Required Python Packages
```bash
pip install -r requirements.txt
```

### Step 5: (Optional) Initialize the Database
The application **automatically initializes the database and seeds 40 sample records** on first launch. If you wish to run the standalone initializer:
```bash
python database/init_db.py
```

---

## 🏃 7. Running the Application

### Option A: From VS Code (One-Click)
1. Open the **Run and Debug** view in VS Code (`Ctrl + Shift + D`).
2. Select **"Python: Run app.py Directly"** or **"Python: Flask (Air Pollution System)"**.
3. Press **F5** (or click the green Play icon).
4. Open your browser and navigate to:  
   👉 **`http://127.0.0.1:5002`**

### Option B: From the Terminal
```bash
python app.py
```

You will see output similar to:
```text
=================================================================
  AIR POLLUTION MONITORING SYSTEM - INTERNSHIP PROJECT
  Web Server running at: http://127.0.0.1:5002
  Dashboard:             http://127.0.0.1:5002/
  Historical Analysis:   http://127.0.0.1:5002/history
  Statistical Analytics: http://127.0.0.1:5002/analytics
  REST API Explorer:     http://127.0.0.1:5002/api-docs
=================================================================
```

---

## 📡 8. REST API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/readings/latest` | Returns latest reading, status, and alerts |
| `GET` | `/api/readings/history` | Paginated historical records (supports `start_date`, `end_date`, `status`, `page`, `per_page`, `limit`) |
| `POST` | `/api/readings` | Ingest manual or hardware sensor reading |
| `GET` | `/api/stats` | Aggregated statistics (min, max, average, status distribution) |
| `GET` | `/api/alerts` | Returns recent alerts triggered by elevated readings |
| `POST` | `/api/simulate` | Triggers immediate simulated reading (supports `{"spike": true}`) |
| `POST` | `/api/simulator/toggle` | Toggles background simulator generator |
| `GET` | `/api/simulator/status` | Current background simulation status |
| `POST` | `/api/seed` | Seeds N historical readings |
| `GET` | `/api/export/csv` | Download complete database history as CSV |

### Testing with cURL / PowerShell:

#### 1. Fetch Latest Reading:
```bash
curl -X GET http://127.0.0.1:5002/api/readings/latest
```

#### 2. Ingest a Sensor Reading:
```bash
curl -X POST http://127.0.0.1:5002/api/readings \
  -H "Content-Type: application/json" \
  -d '{"pm25": 45.2, "co2": 780.0, "temperature": 26.3, "humidity": 53.0}'
```

#### 3. Inject a High Pollution Spike:
```bash
curl -X POST http://127.0.0.1:5002/api/simulate \
  -H "Content-Type: application/json" \
  -d '{"spike": true}'
```

---

## 🧪 9. Automated Testing Procedures

The project includes an automated test suite verifying model classification, alert generation, simulator functionality, and REST API endpoints.

Execute all unit and integration tests with:
```bash
python tests/test_app.py
```

### Expected Output:
```text
Ran 12 tests in 0.3s
OK
```

---

## 🐬 10. Optional: Switching from SQLite to MySQL

By default, the application runs on SQLite (`database/air_pollution.db`) without requiring any database server installation.

If your internship requires a **MySQL** database:
1. Create a database in MySQL:
   ```sql
   CREATE DATABASE air_pollution_db;
   ```
2. Set the `DATABASE_URL` environment variable before running:
   ```bash
   # Windows PowerShell
   $env:DATABASE_URL="mysql+pymysql://username:password@localhost:3306/air_pollution_db"
   
   # Linux / macOS
   export DATABASE_URL="mysql+pymysql://username:password@localhost:3306/air_pollution_db"
   ```
3. Install the PyMySQL driver:
   ```bash
   pip install pymysql
   ```
4. Run `python app.py`. SQLAlchemy will automatically create all tables in MySQL!

---

## 📄 11. Internship Project Report

A complete 20-section project documentation report formatted for academic submission and PDF conversion is provided in:  
📄 **[`PROJECT_REPORT.md`](file:///c:/Users/Admin/Downloads/air%20pollution/PROJECT_REPORT.md)**

---

## 👨‍💻 12. Author & Acknowledgments

- **Project:** Air Pollution Monitoring System
- **Role:** Full-Stack Python Software Engineering Intern
- **Standards Reference:** World Health Organization (WHO) Air Quality Guidelines & Central Pollution Control Board (CPCB / NAAQS)
