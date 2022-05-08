# Image resize api

### Description:
    Resize squared image to 32x32 or 64x64
# *Requests*
### Send image 
    POST /tasks {image: *IMAGE*}
### Get task_status
    GET /tasks/{task_id}
### Get resized image
    GET /tasks/{task_id}/image?size=<64, 32 or original>
___
### Create venv:
    make venv

### Run tests:
    make test

### Run linters:
    make lint

### Run formatters:
    make format
    
### Run app:
    make up
    
# TODO
* Рефакторинг кода в соответствии с принципами SOLID
