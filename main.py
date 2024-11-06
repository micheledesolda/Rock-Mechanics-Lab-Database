# main.py
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from rock_mechanics_lab_database.utils.mongo_utils import is_mongodb_running, start_mongodb
from rock_mechanics_lab_database.api.routers import blocks, core_samples, experiments, gouges, machines, sensors

# Check connection to database is working
if not is_mongodb_running():
    print("MongoDB is not running. Starting MongoDB...")
    start_mongodb()
else:
    print("MongoDB is running.")

app = FastAPI()

# Configure CORS
origins = os.getenv("CORS_ORIGINS", "http://localhost,http://localhost:8000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(blocks.router, prefix="/blocks", tags=["blocks"])
app.include_router(core_samples.router, prefix="/core_samples", tags=["core_samples"])
app.include_router(experiments.router, prefix="/experiments", tags=["experiments"])
app.include_router(gouges.router, prefix="/gouges", tags=["gouges"])
app.include_router(machines.router, prefix="/machines", tags=["machines"])
app.include_router(sensors.router, prefix="/sensors", tags=["sensors"])

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open("static/index.html") as f:
        return HTMLResponse(content=f.read(), status_code=200)

if __name__ == "__main__":
    if not is_mongodb_running():
        print("MongoDB is not running. Starting MongoDB...")
        start_mongodb()
    else:
        print("MongoDB is running.")
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
