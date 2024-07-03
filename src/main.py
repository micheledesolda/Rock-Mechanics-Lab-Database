# src/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import blocks, experiments

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
app.include_router(blocks.router, prefix="/blocks", tags=["blocks"])
app.include_router(experiments.router, prefix="/experiments", tags=["experiments"])

# You can add more routers as needed

# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
