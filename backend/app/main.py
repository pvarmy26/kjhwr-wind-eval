from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
import requests
from datetime import timedelta

app = FastAPI(title="UK Wind Evaluator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ELEXON_BASE_URL = "https://data.elexon.co.uk/bmrs/api/v1"

@app.get("/")
def health_check():
    return {"status": "ok", "message": "Backend is running!"}

def fetch_actuals(date_str: str) -> pd.DataFrame:
    """Fetch actual wind generation from FUELHH dataset for a given settlement date (YYYY-MM-DD)."""
    url = f"{ELEXON_BASE_URL}/datasets/FUELHH/stream"
    params = {
        "settlementDateFrom": date_str,
        "settlementDateTo": date_str,
        "format": "json"
    }
    
    res = requests.get(url, params=params, timeout=15)
    if res.status_code != 200:
        raise HTTPException(status_code=500, detail=f"Failed to fetch actuals: status {res.status_code}")
    
    raw_data = res.json()
    if not raw_data:
        return pd.DataFrame(columns=["startTime", "actual_generation"])
        
    df = pd.DataFrame(raw_data)
    
    # Filter for WIND fuelType
    wind_df = df[df["fuelType"] == "WIND"].copy()
    if wind_df.empty:
        return pd.DataFrame(columns=["startTime", "actual_generation"])
        
    wind_df["startTime"] = pd.to_datetime(wind_df["startTime"], utc=True)
    wind_df = wind_df[["startTime", "generation"]].rename(columns={"generation": "actual_generation"})
    return wind_df

def fetch_forecasts(date_str: str) -> pd.DataFrame:
    """Fetch wind forecasts from WINDFOR dataset for target delivery date and apply gate closure cutoff."""
    url = f"{ELEXON_BASE_URL}/datasets/WINDFOR/stream"
    
    # Query window: 2 days prior to target date up to target date end
    target_dt = pd.to_datetime(date_str, utc=True)
    from_dt = (target_dt - timedelta(days=2)).strftime("%Y-%m-%dT00:00:00Z")
    to_dt = (target_dt + timedelta(days=1)).strftime("%Y-%m-%dT23:59:59Z")
    
    params = {
        "publishDateTimeFrom": from_dt,
        "publishDateTimeTo": to_dt,
        "format": "json"
    }
    
    res = requests.get(url, params=params, timeout=15)
    if res.status_code != 200:
        raise HTTPException(status_code=500, detail=f"Failed to fetch forecasts: status {res.status_code}")
        
    raw_data = res.json()
    if not raw_data:
        return pd.DataFrame(columns=["startTime", "publishTime", "forecast_generation"])
        
    df = pd.DataFrame(raw_data)
    if df.empty:
        return pd.DataFrame(columns=["startTime", "publishTime", "forecast_generation"])
        
    # Standardize datetimes to UTC
    df["startTime"] = pd.to_datetime(df["startTime"], utc=True)
    df["publishTime"] = pd.to_datetime(df["publishTime"], utc=True)
    df = df.rename(columns={"generation": "forecast_generation"})
    
    # Filter for target delivery date (Day D)
    df = df[df["startTime"].dt.strftime("%Y-%m-%d") == date_str]
    
    # Market Cutoff: 11:00 AM UTC on Day-1 (D-1)
    cutoff_dt = target_dt - timedelta(days=1) + timedelta(hours=11)
    
    # Select forecasts published on or before 11:00 AM on D-1
    valid_forecasts = df[df["publishTime"] <= cutoff_dt]
    
    if not valid_forecasts.empty:
        # Take the latest forecast published before cutoff for each 30-min settlement period
        latest = valid_forecasts.sort_values("publishTime").groupby("startTime").last().reset_index()
    else:
        # Fallback to latest available if pre-cutoff data is missing
        latest = df.sort_values("publishTime").groupby("startTime").last().reset_index()
        
    return latest[["startTime", "publishTime", "forecast_generation"]]

@app.get("/api/wind-analysis")
def get_wind_analysis(date: str = Query("2026-01-15", description="Target date in YYYY-MM-DD format")):
    """Calculates actual vs forecast generation and quantitative error metrics."""
    # Handle empty date param edge-case
    if not date or not date.strip():
        date = "2026-01-15"

    try:
        pd.to_datetime(date, format="%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Please use YYYY-MM-DD.")

    actuals_df = fetch_actuals(date)
    forecasts_df = fetch_forecasts(date)
    
    if actuals_df.empty or forecasts_df.empty:
        return {
            "date": date,
            "metrics": None,
            "series": [],
            "message": "No data available for selected date."
        }
    
    merged = pd.merge(actuals_df, forecasts_df, on="startTime", how="inner").sort_values("startTime")
    
    if merged.empty:
        return {
            "date": date,
            "metrics": None,
            "series": [],
            "message": "No matching timestamps between actuals and forecasts."
        }
    
    actuals = merged["actual_generation"].values
    forecasts = merged["forecast_generation"].values
    
    # Quantitative Metrics
    mae = float(np.mean(np.abs(actuals - forecasts)))
    rmse = float(np.sqrt(np.mean((actuals - forecasts) ** 2)))
    bias = float(np.mean(forecasts - actuals))  # Positive = Overforecasting
    
    denom = np.where(actuals == 0, 1e-5, actuals)
    mape = float(np.mean(np.abs((actuals - forecasts) / denom)) * 100)
    
    # Time series output
    merged["time"] = merged["startTime"].dt.strftime("%H:%M")
    series = merged[["time", "actual_generation", "forecast_generation"]].to_dict(orient="records")
    
    return {
        "date": date,
        "metrics": {
            "mae_mw": round(mae, 2),
            "rmse_mw": round(rmse, 2),
            "mape_percent": round(mape, 2),
            "bias_mw": round(bias, 2),
            "status": "Overforecasting" if bias > 0 else "Underforecasting"
        },
        "series": series
    }