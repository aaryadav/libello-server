from fastapi import FastAPI
from app.routers import endpoints
from app.routers import storage
from app.utils import websocket
from config.logger_config import setup_logging

setup_logging()

app = FastAPI()

# Include routers from the routers module
app.include_router(endpoints.router)
app.include_router(websocket.router)
app.include_router(storage.router)

if __name__ == "__main__":
    # Running the app
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)