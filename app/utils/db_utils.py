from uuid import UUID, uuid4
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.utils.r2_utils import *

from app.models.db_model import Notebooks
from config.db_config import SessionLocal
import traceback


def verify_notebook_user(user_id: str, notebook_id: str):
    with SessionLocal() as db:
        notebook = db.query(Notebooks).filter_by(id=notebook_id).first()
        if not notebook or notebook.user_id != user_id:
            raise HTTPException(
                status_code=404, detail="Notebook not found or access denied")

        return notebook


def create_notebook(user_id: str, notebook_name: str):
    try:
        with SessionLocal() as db:

            notebook_id = str(uuid4())

            new_notebook = Notebooks(
                id=notebook_id, user_id=user_id, name=notebook_name)

            db.add(new_notebook)
            db.commit()
            db.refresh(new_notebook)

            # save to r2
            create_notebook_r2(notebook_id)
            print(new_notebook)

            return new_notebook

    # except SQLAlchemyError as e:
    except Exception as e:
        db.rollback()
        print(f"An error occurred during the notebook creation process: {e}")

        print("ERROR INFO: ", traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


def get_notebook_contents(user_id: str, notebook_id: UUID):
    try:
        with SessionLocal() as db:

            notebook = db.query(Notebooks).filter(
                Notebooks.user_id == user_id, Notebooks.id == notebook_id).first()
            if notebook:
                return read_notebook_r2(notebook_id)
            else:
                raise HTTPException(
                    status_code=404, detail="Notebook not found")
    except SQLAlchemyError as e:
        print("ERROR INFO: ", traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


def get_notebooks(user_id: str, skip: int = 0, limit: int = 10):
    try:
        with SessionLocal() as db:

            notebooks = db.query(Notebooks).filter(
                Notebooks.user_id == user_id).offset(skip).limit(limit).all()
            print(notebooks)
            return notebooks
    except SQLAlchemyError as e:
        print("ERROR INFO: ", traceback.format_exc())

        raise HTTPException(status_code=500, detail=str(e))


def update_notebook_content(user_id: str, notebook_id: dict, content: str):
    try:
        with SessionLocal() as db:
            notebook = db.query(Notebooks).filter(
                Notebooks.user_id == user_id, Notebooks.id == notebook_id).first()
            if notebook:
                update_notebook_r2(notebook_id, content)
                return notebook
            else:
                raise HTTPException(
                    status_code=404, detail="Notebook not found")
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


def delete_user_notebook(user_id: str, notebook_id: int):
    try:
        with SessionLocal() as db:
            notebook = db.query(Notebooks).filter(
                Notebooks.user_id == user_id, Notebooks.id == notebook_id).first()
            if notebook:
                db.delete(notebook)
                db.commit()
                delete_notebook_r2(notebook_id)
                return {"detail": "Notebook deleted successfully"}
            else:
                raise HTTPException(
                    status_code=404, detail="Notebook not found")
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
