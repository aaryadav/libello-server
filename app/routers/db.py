from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from uuid import UUID

from app.utils.db_utils import (
    verify_notebook_user, create_notebook, get_notebooks,
    get_notebook_contents, update_notebook_content, delete_user_notebook
)

from app.utils.db_utils import create_notebook, get_notebooks
from app.models.db_model import Notebooks

import logging

from config.fief_config import *
from config.settings import *

router = APIRouter()
logger = logging.getLogger("baljeet")


class NotebookCreate(BaseModel):
    notebook_name: str = Field(..., example="My Notebook")


class NotebookResponse(BaseModel):
    id: UUID
    name: str
    user_id: str

    class Config:
        from_attributes = True


class NotebookContent(BaseModel):
    file_content: str


class NotebookUpdateRequest(BaseModel):
    content: str

# CREATE


@router.post("/notebook")
def create_notebook_endpoint(
    notebook_data: NotebookCreate,
    user: FiefUserInfo = Depends(auth.current_user()),
):
    """
    save a new notebook to the db and r2
    """
    user_id = user["sub"]
    return create_notebook(user_id, notebook_data.notebook_name)


# READ
@router.get("/notebook/{notebook_id}", response_model=NotebookContent)
def read_notebook_endpoint(
    notebook_id: str,
    user: FiefUserInfo = Depends(auth.current_user()),
):
    """
    read a notebook's contents
    """
    user_id = user["sub"]
    verified_notebook = verify_notebook_user(user_id, notebook_id)
    if not verified_notebook:
        raise HTTPException(
            status_code=404, detail="Notebook not found or access denied")
    notebook_contents = get_notebook_contents(user_id, notebook_id)
    print(notebook_contents)
    return notebook_contents


@router.get("/notebooks", response_model=list[NotebookResponse])
def read_notebooks_endpoint(
    user: FiefUserInfo = Depends(auth.current_user()),
    skip: int = 0, limit: int = 10
):
    """
    get a list of notebooks of the user
    """
    user_id = user["sub"]
    notebooks = get_notebooks(user_id, skip, limit)
    return [NotebookResponse.model_validate(notebook) for notebook in notebooks]

# UPDATE


@router.put("/update-notebook/{notebook_id}")
def update_notebook_endpoint(
    notebook_id: str,
    request: NotebookUpdateRequest,
    user: FiefUserInfo = Depends(auth.current_user()),
):
    """
    update the contents of a notebook
    """
    print(request.content)
    user_id = user["sub"]
    verified_notebook = verify_notebook_user(user_id, notebook_id)
    if not verified_notebook:
        raise HTTPException(
            status_code=404, detail="Notebook not found or access denied")

    return update_notebook_content(user_id, notebook_id, request.content)

# DELETE


@router.delete("/delete-notebook/{notebook_id}")
def delete_notebook_endpoint(
    notebook_id: str,
    user: FiefUserInfo = Depends(auth.current_user()),
):
    """
    delete the notebook
    """
    user_id = user["sub"]
    verified_notebook = verify_notebook_user(user_id, notebook_id)
    if not verified_notebook:
        raise HTTPException(
            status_code=404, detail="Notebook not found or access denied")

    return delete_user_notebook(user_id, notebook_id)
