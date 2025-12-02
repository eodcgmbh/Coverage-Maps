import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.templating import Jinja2Templates
import subprocess
import json, tempfile
from src.coverage_map.main import main, get_coll
from datetime import datetime, timedelta
from fastapi.responses import JSONResponse

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")

app = FastAPI()

@app.get("/coverage")
async def coverage(
    from_date: str,
    to_date: str,
    collection: str,
    lonmin: float = -180,
    latmin: float = -90,
    lonmax: float = 180,
    latmax: float = 90,
    download: bool = False,
):
    
    def parse_iso(dt_str):
        clean = dt_str.strip('"').replace("Z", "+00:00")
        return datetime.fromisoformat(clean)

    f_date = parse_iso(from_date)
    t_date = parse_iso(to_date)

    if t_date - f_date >= timedelta(days=365):
        return JSONResponse(
            content={
                "error": "Invalid time range",
                "message": (
                    "The selected time range is too long. "
                    "Please choose a date range that does not exceed one year "
                    "(365 days) to ensure optimal performance and avoid timeouts."
                ),
                "details": {
                    "from_date": from_date,
                    "to_date": to_date,
                    "max_allowed_range_days": 365
                }
            },
            status_code=400
        )

    
    
    result = main(from_date, to_date, collection, lonmin, latmin, lonmax, latmax)

    if download:
        tmp = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json")  # <-- note mode="w"
        json.dump(result, tmp)
        tmp.close()
        return FileResponse(tmp.name, filename="coverage.json")

    return result

@app.get("/")
def root():
    return {"message": "Server is running! Try /coverage"}

@app.get("/collection")
async def collection():
    result = get_coll()
    return result

@app.get("/coverage/map", response_class=HTMLResponse)
async def map_page(request: Request):
    api_base = os.environ.get("API_BASE_URL")
    return templates.TemplateResponse(
        "map.html",
        {"request": request, "api_base": api_base}
    )

