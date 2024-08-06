FROM python:3.10

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt
COPY ./.env /code/.env

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./res /code/res
COPY ./server.py /code/

CMD ["fastapi", "run", "server.py", "--port", "80"]