from pydantic import BaseModel, Field
from typing import List


class CreateProjectRequest(BaseModel):
    project_name: str = Field(..., min_length=1,
                              description="The name of the project.", example="megatest")
    project_dependencies: List[str] = Field(
        default=[], description="A list of dependencies required by the project.", example=["numpy"])


class CreateNotebookRequest(BaseModel):
    project_id: int = Field(...,
                            description="The ID of the project for which the notebook is being created.")
    notebook_name: str = Field(..., min_length=1,
                               description="The name of the notebook.")


class RunRequest(BaseModel):
    container_id: str = Field(..., description="Container's ID" )
    notebook_id: int = Field(...,
                             description="Notebook's ID")
