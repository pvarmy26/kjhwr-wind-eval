# UK Wind Generation Forecast Evaluator

A customized web application developed for UK energy utilities to evaluate day-ahead wind power generation forecasts against actual outturn data from Elexon BMRS for January 2026.

## Live Application
- **Frontend App (Vercel):** https://kjhwr-wind-eval.vercel.app
- **Backend API Docs (Render):** https://kjhwr-wind-eval.onrender.com/docs

## AI Tools Disclosure
- **Gemini / AI Coding Assistant:** Used for rapid full-stack scaffolding, Elexon BMRS endpoint integration, UI/CSS dark mode styling, and metrics calculation verification.

## 📁 Repository & Directory Structure
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

## Local Setup

```bash
# Clone the repository
git clone [https://github.com/pvarmy26/kjhwr-wind-eval.git](https://github.com/pvarmy26/kjhwr-wind-eval.git)
cd kjhwr-wind-eval

# Start services via Docker
docker-compose up --build




