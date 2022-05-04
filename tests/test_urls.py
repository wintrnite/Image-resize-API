from http import HTTPStatus
from json import loads

import pytest

from app.constants import RedisKey, TaskStatus
from tests.conftest import get_task_id_from_url


def test_send_picture(send_picture_response, fake_redis):
    response_json = loads(send_picture_response.content)
    task_status = response_json['task_status']
    task_id = response_json['task_id']
    assert send_picture_response.status_code == HTTPStatus.CREATED
    assert task_status == TaskStatus.DONE.value
    assert (
        fake_redis.hget(str(task_id), RedisKey.TASK_STATUS.value).decode('utf-8')
        == TaskStatus.DONE.value
    )


def test_get_task_status(get_task_status_response, fake_redis):
    response_json = loads(get_task_status_response.content)
    task_status_from_response = response_json['task_status']
    task_id = get_task_id_from_url(get_task_status_response.url)
    task_status_from_db = fake_redis.hget(task_id, RedisKey.TASK_STATUS.value).decode(
        'utf-8'
    )
    assert get_task_status_response.status_code == HTTPStatus.OK
    assert task_status_from_response == task_status_from_db


@pytest.mark.parametrize('size', [32, 64, 'original'])
def test_receive_resized_image(size, get_task_status_response, test_client):
    task_id = get_task_id_from_url(get_task_status_response.url)
    response = test_client.get(f'/tasks/{task_id}/image?size={size}')
    assert response.status_code == HTTPStatus.OK


def test_receive_resized_image_with_bad_size(get_task_status_response, test_client):
    task_id = get_task_id_from_url(get_task_status_response.url)
    bad_size = 63
    response = test_client.get(f'/tasks/{task_id}/image?size={bad_size}')
    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_send_not_picture(send_not_picture_response):
    assert send_not_picture_response.status_code == HTTPStatus.BAD_REQUEST
