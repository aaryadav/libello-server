import atexit
import json
from config.redis_config import *
from config.docker_config import *
from app.utils.websocket import *
from fastapi import APIRouter

router = APIRouter()

async def update_container_status(user_id: str, container_id: str, new_status: str, port: int):
    status_and_port = {
        'status': new_status,
        'port': port
    }
    redis_client.hset(f"user:{user_id}:containers",
                      container_id, json.dumps(status_and_port))

    # Send a WebSocket message to the user with the updated status
    await send_status_update(user_id, container_id, new_status)

@router.get("/clean-it-up-baljeet")
def cleanup_containers():
    # Iterate through each user hash key
    for key in redis_client.scan_iter("user:*:containers"):
        # Retrieve all container IDs for the user
        all_containers = redis_client.hgetall(key)
        for container_id_bytes in all_containers.keys():
            container_id = container_id_bytes.decode('utf-8')
            try:
                container = docker_client.containers.get(container_id)
                print(f"Stopping container {container_id}")
                container.stop()
                container.remove()
            except docker.errors.NotFound:
                print(
                    f"Container {container_id} not found, it might have been stopped already.")
            except Exception as e:
                print(f"Error stopping container {container_id}: {e}")

        # After processing all containers, delete the user's hash
        redis_client.delete(key)


atexit.register(cleanup_containers)