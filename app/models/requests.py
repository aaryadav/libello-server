from pydantic import BaseModel, Field
from typing import List


class CreateProjectRequest(BaseModel):
    project_name: str = Field(..., min_length=1,
                              description="The name of the project.", example="megatest")
    project_dependencies: List[str] = Field(
        default=[], description="A list of dependencies required by the project.", example=["numpy"])


class CreateSessionRequest(BaseModel):
    container_id: str = Field(...,
                              description="Container ID")
    session_name: str = Field(..., min_length=1,
                              description="The name of the session.")

class RunRequest(BaseModel):
    container_id: str = Field(..., description="Container's ID")
    session_id: int = Field(...,
                            description="Session ID")
    kernel_id: int = Field(...,
                           description="Kernel ID")


class ExecRequest(BaseModel):
    container_id: str
    kernel_id: str
    session_id: str
    code: str
