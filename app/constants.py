from enum import Enum


class TaskStatus(Enum):
    WAITING = 'WAITING'
    IN_PROGRESS = 'IN_PROGRESS'
    DONE = 'DONE'
    FAILED = 'FAILED'


class ImageSize(Enum):
    ORIGINAL = 'original'
    PIXELS_32 = '32'
    PIXELS_64 = '64'


class RedisKey(Enum):
    TASK_STATUS = 'task_status'
    ORIGINAL = 'original'
    SIZE_64 = '64'
    SIZE_32 = '32'


class ErrorMessage(Enum):
    INCORRECT_IMAGE_SIZE = 'incorrect image size!'
    INCORRECT_TASK_ID = 'incorrect task id!'
    INCORRECT_IMAGE_FORMAT = 'incorrect image format!'
    NOT_IMAGE = 'not an image!'
    IMAGE_NOT_FOUND = 'image was not found'
