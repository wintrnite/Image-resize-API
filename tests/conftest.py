# pylint: disable=redefined-outer-name

from io import BytesIO
from json import loads
from urllib.parse import urlparse

import pytest
from fakeredis import FakeStrictRedis
from fastapi.testclient import TestClient
from PIL import Image
from rq import Queue

from app.app import app
from app.settings import Settings


@pytest.fixture(scope='session')
def fake_redis():
    return FakeStrictRedis()


@pytest.fixture(scope='session')
def test_client():
    client = TestClient(app)
    return client


@pytest.fixture(scope='session')
def fake_task_queue(fake_redis):
    queue = Queue(connection=fake_redis, is_async=False)
    return queue


@pytest.fixture(autouse=True)
def _mock_db(mocker, fake_redis, fake_task_queue):
    mocker.patch('app.db.redis_conn', fake_redis)
    mocker.patch('app.urls.redis_conn', fake_redis)
    mocker.patch('app.image_utils.redis_conn', fake_redis)
    mocker.patch('app.db.queue', fake_task_queue)
    mocker.patch('app.urls.queue', fake_task_queue)


@pytest.fixture()
def send_picture_response(test_client: TestClient):
    img = Image.new('RGB', size=(250, 250))
    buffered_image = BytesIO()
    img.save(buffered_image, Settings().return_image_format)
    buffered_image.seek(0)
    response = test_client.post('/tasks', files={'image': buffered_image})
    return response


@pytest.fixture()
def get_task_status_response(send_picture_response, test_client):
    task_id = loads(send_picture_response.content)['task_id']
    response = test_client.get(f'/tasks/{task_id}')
    return response


@pytest.fixture()
def send_not_picture_response(test_client):
    response = test_client.post('/tasks', files={'image': 'shrek'})
    return response


def get_task_id_from_url(url):
    return urlparse(url).path.split('/')[2]
