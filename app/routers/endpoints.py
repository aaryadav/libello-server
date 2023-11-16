import json

from fastapi import Depends, HTTPException, APIRouter
from fastapi.responses import StreamingResponse

from typing import Optional
import logging

from app.utils.docker_manager import *
from app.models.requests import *
from config.docker_config import *
from config.fief_config import *
from config.redis_config import *

from app.utils.kernel import *

router = APIRouter()

logger = logging.getLogger("baljeet")

@router.get("/")
def hello(
    user: FiefUserInfo = Depends(auth.current_user())
):
    logger.info("Ayo! who dis")
    print(user["sub"])


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
    print(request)
    print(user["sub"])
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
    await update_container_status(user_id, container.short_id, container.status, assigned_port)

    return {
        "message": "Project created successfully",
        "user_id": user_id,
        "container_id": container.short_id
    }


@router.get("/health-check")
def health_check(
    container_id: Optional[str] = None,
    user: FiefUserInfo = Depends(auth.current_user())
):
    user_id = user["sub"]
    container_status_key = f"user:{user_id}:containers"

    try:
        # Retrieve all container statuses
        container_statuses = redis_client.hgetall(container_status_key)
        if not container_statuses:
            return {"message": "No containers found for this user."}

        if container_id:
            # Check for a specific container's status
            status_info = container_statuses.get(container_id.encode())
            if not status_info:
                return {"error": f"Container {container_id} status not found"}

            status_info = json.loads(status_info.decode('utf-8'))
            return {
                "container_id": container_id,
                "status": status_info["status"],
                "port": status_info["port"]
            }
        else:
            # Return status for all containers
            return {
                key.decode('utf-8'): json.loads(value.decode('utf-8'))
                for key, value in container_statuses.items()
            }

    except docker.errors.NotFound:
        return {"error": "Container not found"}
    except docker.errors.APIError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))


@router.post("/create-notebook")
def create_notebook(
    request: CreateNotebookRequest,
    user: FiefUserInfo = Depends(auth.current_user())
):
    """
    - user_id
    - project_id
    - get container id from redis store
    - start jupyter session
    - create notebook
    """
    return request


@router.post("/run")
async def run(
    request: RunRequest,
    user: FiefUserInfo = Depends(auth.current_user())
):
    """
    - user_id
    - project_id
    - get session deets from redis
    - run code
    """
    user_id = user["sub"] 
    # user_id = "07bbdadf-1322-4388-a861-304fd82c62db"
    container_status_key = f"user:{user_id}:containers"
    container_id = request.container_id
    notebook_name = "notebooks/new_note.ipynb"
    container_port = json.loads(redis_client.hget(
        container_status_key, container_id).decode('utf-8'))["port"]
    url = f"http://localhost:{container_port}/"
    token = ""
    res, session = connect(url, token)
    
    data = create_session(session, url, notebook_name)
    print(data)
    kernel_id = data["kernel"]["id"]
    session_id = data["id"]
    print(kernel_id, session_id)

    data = get_contents(session, url, notebook_name)
    async def generate_output():
        for cell in data["content"]["cells"]:
            code = cell["source"]
            # exec_code is a generator function which yields the output of the code
            # print the output of the code
            for output in exec_code(url, token, kernel_id, session_id, code):
                yield output
    
    return StreamingResponse(generate_output(), media_type="text/event-stream")
