import json

from fastapi import Depends, HTTPException, APIRouter
from fastapi.responses import StreamingResponse
from fastapi import HTTPException

import time
from typing import Optional, Tuple
import logging

from app.utils.docker_manager import *
from app.models.requests import *
from config.docker_config import *
from config.fief_config import *
from config.redis_config import *
from redis.exceptions import ConnectionError
from sse_starlette.sse import EventSourceResponse


from app.utils.kernel import *

router = APIRouter()

logger = logging.getLogger("baljeet")

MAX_RETRIES = 5
WAIT_SECONDS = 2


@router.post("/create-project")
async def create_project(
    request: CreateProjectRequest,
    user: FiefUserInfo = Depends(auth.current_user())
):
    """
    - user_id
    - project_name
    - project_dependencies
    """
    user_id = user["sub"]
    try:

        # Convert the dependencies list to a comma-separated string
        dependencies = ",".join(request.project_dependencies)

        # Start docker container with PROJECT_DEPENDENCIES environment variable
        container = docker_client.containers.run(
            'jupyter-base',
            detach=True,
            ports={'8888/tcp': None},
            volumes={
                '/home/aaryaman/mycode/libello-server/': {
                    'bind': '/notebooks',
                    'mode': 'rw',
                },
            },
            environment={
                'PROJECT_DEPENDENCIES': dependencies
            }
        )

        container.reload()
        print(container.status)

    except docker.errors.APIError as e:
        print(f"Error executing command: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    assigned_port = container.attrs['NetworkSettings']['Ports']['8888/tcp'][0]['HostPort']
    print(assigned_port)

    retry_count = 0
    while retry_count < MAX_RETRIES:
        try:
            # Place the Redis operation here
            await update_container_status(user_id, container.short_id, container.status, assigned_port)
            break  # Break the loop if operation is successful
        except ConnectionError as e:
            print(
                f"Redis connection error: {e}, retrying ({retry_count + 1}/{MAX_RETRIES})")
            time.sleep(WAIT_SECONDS)  # Wait for a bit before retrying
            retry_count += 1

    if retry_count == MAX_RETRIES:
        raise HTTPException(
            status_code=503,
            detail="Currently unable to process the request. Please try again later."
        )

    return {
        "message": "Project created successfully",
        "user_id": user_id,
        "container_id": container.short_id
    }


@router.post("/create-session")
def create_session(
    request: CreateSessionRequest,
    user: FiefUserInfo = Depends(auth.current_user())
):
    user_id = user["sub"]
    container_status_key = f"user:{user_id}:containers"
    container_id = request.container_id
    notebook_name = "notebooks/new_note.ipynb"

    # Retrieve container port from Redis
    container_port = json.loads(redis_client.hget(
        container_status_key, container_id).decode('utf-8'))["port"]

    url = f"http://localhost:{container_port}/"
    token = ""

    # Create session
    print("ALL OK")
    res, session = connect(url, token)
    print("ALL OK")

    data = create_kernel_session(session, url, notebook_name)
    # Extracting kernel and session ID
    kernel_id = data["kernel"]["id"]
    session_id = data["id"]

    return {"kernel_id": kernel_id, "session_id": session_id}


@router.post("/execute-code")
def execute_code_in_session(
    request: ExecRequest,
    user: FiefUserInfo = Depends(auth.current_user())
):
    print(request)
    user_id = user["sub"]
    token = ""
    container_id = request.container_id
    kernel_id = request.kernel_id
    session_id = request.session_id
    code = request.code

    container_status_key = f"user:{user_id}:containers"
    container_port = json.loads(redis_client.hget(
        container_status_key, container_id).decode('utf-8'))["port"]
    url = f"http://localhost:{container_port}/"

    def generate_output():
        for message in exec_code(url, token, kernel_id, session_id, code):
            yield message + "\n"

    return EventSourceResponse(generate_output())
