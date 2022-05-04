from base64 import b64decode
from http import HTTPStatus
from io import BytesIO
from typing import Any

import uvicorn
from fastapi import HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from PIL import Image, UnidentifiedImageError

from app.app import app
from app.constants import ErrorMessage, RedisKey, TaskStatus
from app.db import queue, redis_conn
from app.image_utils import (
    get_base64_encoded_image,
    image_size_is_correct,
    resize_squared_image,
)
from app.response_models import CreatedTaskResponse, TaskStatusResponse
from app.settings import Settings


@app.post('/tasks', status_code=HTTPStatus.CREATED)
def create_task(image: UploadFile) -> CreatedTaskResponse:
    image_id = redis_conn.dbsize()
    try:
        with Image.open(image.file) as original_image:
            width, height = original_image.size
            if width != height:
                raise HTTPException(
                    status_code=HTTPStatus.BAD_REQUEST,
                    detail=ErrorMessage.INCORRECT_IMAGE_SIZE.value,
                )
            encoded_image = get_base64_encoded_image(original_image)
            redis_conn.hset(str(image_id), RedisKey.ORIGINAL.value, encoded_image)
            redis_conn.hset(
                str(image_id),
                RedisKey.TASK_STATUS.value,
                TaskStatus.WAITING.value,
            )
    except UnidentifiedImageError as not_image:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=ErrorMessage.NOT_IMAGE.value,
        ) from not_image
    queue.enqueue(resize_squared_image, image_id, 32)
    queue.enqueue(resize_squared_image, image_id, 64)
    response = CreatedTaskResponse(
        task_id=image_id,
        task_status=redis_conn.hget(str(image_id), RedisKey.TASK_STATUS.value),
    )
    return response


@app.get('/tasks/{task_id}')
def get_task_status(task_id: int) -> TaskStatusResponse:
    task_status = redis_conn.hget(str(task_id), RedisKey.TASK_STATUS.value)
    if not task_status:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=ErrorMessage.INCORRECT_TASK_ID.value,
        )
    return TaskStatusResponse(task_status=task_status)


@app.get('/tasks/{task_id}/image', response_class=StreamingResponse)
def get_image(task_id: int, size: str) -> Any:
    if not image_size_is_correct(size):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=ErrorMessage.INCORRECT_IMAGE_SIZE.value,
        )
    decoded_return_picture = redis_conn.hget(str(task_id), size)
    if decoded_return_picture is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=ErrorMessage.IMAGE_NOT_FOUND.value,
        )
    return StreamingResponse(
        BytesIO(b64decode(decoded_return_picture)),
        media_type=Settings().response_media_type,
    )


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
