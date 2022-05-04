from redis import StrictRedis
from rq import Queue

from app.settings import Settings

redis_conn = StrictRedis(host=Settings().redis_host, port=Settings().redis_port)
queue = Queue(name=Settings().task_queue_name, connection=redis_conn)
