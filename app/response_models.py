from pydantic import BaseModel


class CreatedTaskResponse(BaseModel):
    task_id: int
    task_status: str


class TaskStatusResponse(BaseModel):
    task_status: str
