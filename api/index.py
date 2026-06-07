from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import numpy as np
import pandas as pd

app = FastAPI()

# 1. Enable CORS for POST requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["*"],
)

# 2. TELEMETRY DATA STORAGE
# TODO: Paste your downloaded telemetry rows into this list.
# Ensure each item matches this format: {"region": "apac", "latency_ms": 150, "uptime": 1}
TELEMETRY_DATA: List[Dict[str, Any]] = [
    # --- PASTE YOUR BUNDLE DATA HERE ---
    {"region": "apac", "latency_ms": 150, "uptime": 1},
    {"region": "apac", "latency_ms": 190, "uptime": 0},
    {"region": "amer", "latency_ms": 120, "uptime": 1},
    {"region": "amer", "latency_ms": 200, "uptime": 1},
    # ------------------------------------
]

class MetricRequest(BaseModel):
    regions: List[str]
    threshold_ms: float

@app.post("/")
async def get_metrics(payload: MetricRequest):
    if not TELEMETRY_DATA:
        return {}
        
    df = pd.DataFrame(TELEMETRY_DATA)
    
    # Filter for only the requested regions
    df_filtered = df[df['region'].isin(payload.regions)]
    
    response_data = {}
    
    # Calculate metrics for each region requested
    for region in payload.regions:
        region_df = df_filtered[df_filtered['region'] == region]
        
        if region_df.empty:
            continue
            
        latencies = region_df['latency_ms'].to_numpy()
        uptimes = region_df['uptime'].to_numpy()
        threshold = payload.threshold_ms
        
        # Calculate exactly what your product manager requested
        avg_latency = float(np.mean(latencies))
        p95_latency = float(np.percentile(latencies, 95))
        avg_uptime = float(np.mean(uptimes))
        breaches = int(np.sum(latencies > threshold))
        
        response_data[region] = {
            "avg_latency": avg_latency,
            "p95_latency": p95_latency,
            "avg_uptime": avg_uptime,
            "breaches": breaches
        }
        
    return response_data
