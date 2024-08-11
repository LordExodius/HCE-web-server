FROM python:3.10

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./deploy.sh /code/deploy.sh
COPY ./res /code/res
COPY ./server.py /code/
COPY ./.env /code/.env

RUN chmod 777 /code/deploy.sh

CMD ["/code/deploy.sh"]