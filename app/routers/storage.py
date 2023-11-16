from fastapi import Depends, HTTPException, APIRouter
from fastapi.responses import JSONResponse
from app.utils.cloud.google_drive import GoogleDrive
from app.utils.cloud.config import GoogleDriveConfig
from fastapi.responses import StreamingResponse

import logging

from config.fief_config import *
from config.settings import *

router = APIRouter()
logger = logging.getLogger("baljeet")

config = GoogleDriveConfig(
    CLIENT_ID_JSON=settings.client_id_json,
    SCOPES=settings.scopes,
    STORAGE_JSON=settings.storage_json
)

gdrive = GoogleDrive(config)

@router.get("/list-colab-files")
async def list_files():
    folder_query = "mimeType='application/vnd.google.colaboratory'"

    colab_files  = await gdrive.list_files(folder_query)
    files = await gdrive.list_files(colab_files)

    return JSONResponse(status_code=200, content=colab_files)

@router.get("/import-from-drive")
async def download_file():
    folder_query = "mimeType='application/vnd.google.colaboratory'"

    colab_files  = await gdrive.list_files(folder_query)
    files = await gdrive.list_files(colab_files)
    # write code to save to gcp bucket as {user-id}/colab/{filename}
 
    return JSONResponse(status_code=200, content=colab_files)
