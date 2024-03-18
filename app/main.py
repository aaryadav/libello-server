from fastapi import FastAPI
from app.routers import endpoints
from app.routers import db
from app.utils import websocket
from config.logger_config import setup_logging
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost:3000",
]

setup_logging()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers from the routers module
app.include_router(endpoints.router)
app.include_router(websocket.router)
app.include_router(db.router)

if __name__ == "__main__":
    # Running the app
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)