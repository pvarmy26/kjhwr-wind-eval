from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import requests
import math
from datetime import datetime, timedelta

app = FastAPI(title="UK Wind Evaluator API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ELEXON_BASE_URL = "https://data.elexon.co.uk/bmrs/api/v1"

@app.get("/", summary="Health Check")
def read_root():
    return {"status": "online", "message": "UK Wind Forecast Evaluator API"}

@app.get("/api/wind/actuals", summary="Get Actual Wind Generation")
def get_actual_wind_generation(
    from_date: str = Query(default=None, description="ISO datetime e.g. 2026-01-15T00:00:00Z"),
    to_date: str = Query(default=None, description="ISO datetime e.g. 2026-01-15T23:59:59Z")
):
    if not from_date or not to_date:
        now = datetime.utcnow()
        to_date = now.strftime("%Y-%m-%dT23:59:59Z")
        from_date = (now - timedelta(days=1)).strftime("%Y-%m-%dT00:00:00Z")

    url = f"{ELEXON_BASE_URL}/datasets/FUELHH/stream"
    params = {
        "publishDateTimeFrom": from_date,
        "publishDateTimeTo": to_date,
        "format": "json"
    }

    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        raw_data = response.json() if isinstance(response.json(), list) else response.json().get("data", [])

        wind_actuals = [
            {
                "startTime": item.get("startTime"),
                "generation": item.get("generation"),
                "fuelType": item.get("fuelType")
            }
            for item in raw_data
            if str(item.get("fuelType")).upper() == "WIND"
        ]

        return {"count": len(wind_actuals), "data": wind_actuals}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch actuals: {str(e)}")

@app.get("/api/wind/forecasts", summary="Get Forecasted Wind Generation")
def get_wind_generation_forecast(
    from_date: str = Query(default=None, description="ISO datetime e.g. 2026-01-15T00:00:00Z"),
    to_date: str = Query(default=None, description="ISO datetime e.g. 2026-01-15T23:59:59Z")
):
    if not from_date or not to_date:
        now = datetime.utcnow()
        to_date = now.strftime("%Y-%m-%dT23:59:59Z")
        from_date = (now - timedelta(days=1)).strftime("%Y-%m-%dT00:00:00Z")

    url = f"{ELEXON_BASE_URL}/datasets/WINDFOR/stream"
    params = {
        "publishDateTimeFrom": from_date,
        "publishDateTimeTo": to_date,
        "format": "json"
    }

    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        raw_data = response.json() if isinstance(response.json(), list) else response.json().get("data", [])

        forecasts = [
            {
                "startTime": item.get("startTime"),
                "publishTime": item.get("publishTime"),
                "generation": item.get("generation")
            }
            for item in raw_data
        ]

        return {"count": len(forecasts), "data": forecasts}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch forecasts: {str(e)}")

@app.get("/api/wind-analysis", summary="Get Wind Analysis")
def get_wind_analysis(
    date: str = Query(default="2026-01-15", description="Date string YYYY-MM-DD")
):
    from_date = f"{date}T00:00:00Z"
    to_date = f"{date}T23:59:59Z"

    # 1. Retrieve Actuals
    actuals_resp = get_actual_wind_generation(from_date=from_date, to_date=to_date)
    actuals_data = actuals_resp.get("data", [])

    actuals_map = {}
    for item in actuals_data:
        st = item.get("startTime", "")
        # Filter top-of-hour timestamps e.g. "2026-01-15T00:00:00Z"
        if ":00:00" in st:
            time_str = st[11:16]  # "00:00"
            actuals_map[time_str] = item.get("generation", 0)

    # 2. Retrieve Forecasts and extract the latest publishTime for each startTime
    forecasts_resp = get_wind_generation_forecast(from_date=from_date, to_date=to_date)
    forecasts_data = forecasts_resp.get("data", [])

    forecasts_by_start = {}
    for item in forecasts_data:
        st = item.get("startTime", "")
        pub = item.get("publishTime", "")
        gen = item.get("generation", 0)

        if st.startswith(date):
            time_str = st[11:16]
            if time_str not in forecasts_by_start or pub > forecasts_by_start[time_str]["pub"]:
                forecasts_by_start[time_str] = {"pub": pub, "gen": gen}

    forecasts_map = {k: v["gen"] for k, v in forecasts_by_start.items()}

    # 3. Match Hourly Series and compute performance metrics
    series = []
    errors = []
    abs_errors = []
    sq_errors = []
    pct_errors = []

    for h in range(24):
        time_key = f"{h:02d}:00"
        actual = actuals_map.get(time_key)
        forecast = forecasts_map.get(time_key)

        if actual is not None and forecast is not None:
            series.append({
                "time": time_key,
                "actual_generation": round(actual),
                "forecast_generation": round(forecast)
            })

            err = forecast - actual
            errors.append(err)
            abs_errors.append(abs(err))
            sq_errors.append(err ** 2)
            if actual != 0:
                pct_errors.append(abs(err / actual) * 100)

    if not errors:
        return {
            "date": date,
            "metrics": {
                "mae_mw": 0,
                "rmse_mw": 0,
                "mape_percent": 0,
                "bias_mw": 0,
                "status": "No Data"
            },
            "series": []
        }

    n = len(errors)
    mae = round(sum(abs_errors) / n, 2)
    rmse = round(math.sqrt(sum(sq_errors) / n), 2)
    mape = round(sum(pct_errors) / len(pct_errors), 2) if pct_errors else 0
    bias = round(sum(errors) / n, 2)
    status = "Overforecasting" if bias > 0 else ("Underforecasting" if bias < 0 else "Accurate")

    return {
        "date": date,
        "metrics": {
            "mae_mw": mae,
            "rmse_mw": rmse,
            "mape_percent": mape,
            "bias_mw": bias,
            "status": status
        },
        "series": series
    }