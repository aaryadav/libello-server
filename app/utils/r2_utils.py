import json
from config.r2_config import r2
from botocore.exceptions import ClientError
from fastapi import HTTPException
from botocore.exceptions import NoCredentialsError, ClientError

BUCKET_NAME = 'libello'

def create_notebook_r2(notebook_id: str):
    """
    Save a notebook to r2
    """
    notebook_json = {}
    notebook_bytes = json.dumps(notebook_json).encode('utf-8')
    r2.put_object(Body=notebook_bytes, Bucket=BUCKET_NAME,
                  Key=f'{notebook_id}.ipynb')


def read_notebook_r2(notebook_id: str):
    """
    Read contents of a notebook from r2 
    """
    try:
        response = r2.get_object(
            Bucket=BUCKET_NAME, Key=f"{notebook_id}.ipynb")
        file_content = response['Body'].read()
        return {"file_content": file_content}

    except NoCredentialsError:
        raise HTTPException(
            status_code=500, detail="Credentials not available")
    except ClientError as e:
        raise HTTPException(status_code=404, detail=str(e))


def update_notebook_r2(notebook_id: str, content: str):
    """
    Update contents of an existing notebook in r2
    """
    try:
        print(content)
        r2.put_object(Body=content, Bucket=BUCKET_NAME,
                      Key=f"{notebook_id}.ipynb")
        print("Ayo")
        return "Notebook updated successfully"
    except NoCredentialsError:
        return "Error: AWS credentials not found"
    except ClientError as e:
        return f"An error occurred: {e}"


def delete_notebook_r2(notebook_id: str):
    """
    Delete notebook
    """
    try:
        r2.delete_object(Bucket=BUCKET_NAME, Key=f"{notebook_id}.ipynb")
        return "Notebook deleted successfully"
    except NoCredentialsError:
        return "Error: AWS credentials not found"
    except ClientError as e:
        return f"An error occurred: {e}"
