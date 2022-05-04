from base64 import b64decode, b64encode
from io import BytesIO

from fastapi import HTTPException
from PIL import Image

from app.constants import ErrorMessage, ImageSize, RedisKey, TaskStatus
from app.db import redis_conn
from app.settings import Settings


def image_size_is_correct(image_size: str) -> bool:
    return image_size in (
        ImageSize.ORIGINAL.value,
        ImageSize.PIXELS_32.value,
        ImageSize.PIXELS_64.value,
    )


def resize_squared_image(img_id: int, img_size: int) -> None:
    img_id_str = str(img_id)
    if img_size not in (64, 32):
        redis_conn.hset(img_id_str, RedisKey.TASK_STATUS.value, TaskStatus.FAILED.value)
        raise ValueError(ErrorMessage.INCORRECT_IMAGE_SIZE.value)
    redis_conn.hset(
        img_id_str, RedisKey.TASK_STATUS.value, TaskStatus.IN_PROGRESS.value
    )
    buffered_image = redis_conn.hget(img_id_str, RedisKey.ORIGINAL.value)
    if not buffered_image:
        raise HTTPException(status_code=404, detail=ErrorMessage.IMAGE_NOT_FOUND.value)
    image = BytesIO(b64decode(buffered_image))
    with Image.open(image) as img:
        resized_img = img.resize((img_size, img_size))
    redis_conn.hset(img_id_str, str(img_size), get_base64_encoded_image(resized_img))
    if (
        redis_conn.hget(img_id_str, RedisKey.ORIGINAL.value) is not None
        and redis_conn.hget(img_id_str, RedisKey.SIZE_64.value) is not None
        and redis_conn.hget(img_id_str, RedisKey.SIZE_32.value) is not None
    ):
        redis_conn.hset(img_id_str, RedisKey.TASK_STATUS.value, TaskStatus.DONE.value)


def get_base64_encoded_image(image: Image) -> bytes:
    buffered_image = BytesIO()
    image.save(buffered_image, Settings().return_image_format)
    buffered_image.seek(0)
    return b64encode(buffered_image.getvalue())
