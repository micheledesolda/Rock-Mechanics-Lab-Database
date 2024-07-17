# main.py

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from api.routers import experiments
from fastapi.responses import HTMLResponse
from utils.mongo_utils import is_mongodb_running, start_mongodb


# Check connection to databse is working
if not is_mongodb_running():
    print("MongoDB is not running. Starting MongoDB...")
    start_mongodb()
else:
    print("MongoDB is running.")

app = FastAPI()

# Configure CORS
origins = [
    "http://localhost",
    "http://localhost:8000",
    # Add other origins as needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(experiments.router, prefix="/experiments", tags=["experiments"])

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open("static/index.html") as f:
        return HTMLResponse(content=f.read(), status_code=200)
    

# this is in case I want to run directly main.py. But at the moment, since I run the code with the combo:
#       pip install e .
#       uvicorn src.main:app --reload
# from terminal, there is no need for it
if __name__ == "__main__":
    # Check connection to databse is working
    if not is_mongodb_running():
        print("MongoDB is not running. Starting MongoDB...")
        start_mongodb()
    else:
        print("MongoDB is running.")
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
