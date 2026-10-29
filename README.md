# UK Day-Ahead Wind Forecast Evaluation Portal

A customized full-stack analytical web portal designed for UK energy utility trading teams. The portal enables traders to evaluate national renewable (wind) generation forecasts against Elexon actuals for Day-Ahead electricity purchasing decisions in January 2026.

---

## 🚀 Live Deployment
- **Frontend Web App (Vercel):** [https://your-app.vercel.app](https://your-app.vercel.app) *(Replace with your live Vercel URL)*
- **Backend API Docs (Render/Heroku):** [https://your-backend.onrender.com/docs](https://your-backend.onrender.com/docs) *(Replace with your live Backend URL)*

---

## 🤖 Explicit Declaration of AI Tools Used
In accordance with Section 2 of the assessment guidelines, **AI tool (Gemini)** is explicitly used to assist in building this application. Specifically:
- **Boilerplate & Configuration Generation:** Scaffolding initial FastAPI routes, React Vite structure, and Docker multi-stage builds.
- **Data Engineering Assistance:** Refining Pandas datetime parsing and timezone alignment (`UTC`) for Elexon BMRS API streams.
- **Frontend Visualization Layout:** Styling KPI metric cards and configuring Recharts time-series line chart components.

---

## 📁 Repository & Directory Structure

```text
uk-wind-eval-app/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   └── main.py          # FastAPI server, Elexon API integrations, gate closure cutoff logic, metrics calculation
│   ├── Dockerfile           # Python 3.12-slim production container
│   └── requirements.txt     # FastAPI, Uvicorn, Pandas, NumPy, Requests
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # React dashboard with interactive date picker, metric cards, and Recharts plot
│   │   ├── main.jsx         # React application entry point
│   │   └── index.css        # Dashboard styling
│   ├── Dockerfile           # Multi-stage Docker build (Node build + Nginx server)
│   ├── package.json         # React & Recharts dependencies
│   ├── vite.config.js       # Vite build configuration
│   └── .dockerignore
├── docker-compose.yml       # Multi-container orchestration (Backend + Frontend)
└── README.md                # Project documentation