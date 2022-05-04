from pydantic import BaseSettings


class Settings(BaseSettings):
    return_image_format: str = 'PNG'
    redis_host: str = 'redis'
    redis_port: int = 6379
    app_host: str = '0.0.0.0'
    app_port: int = 8000
    task_queue_name: str = 'image_resize'
    response_media_type: str = 'image/png'
