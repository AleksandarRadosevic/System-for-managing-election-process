FROM python:3

RUN mkdir -p /opt/src/dameon
WORKDIR /opt/src/dameon

COPY dameon/application.py ./application.py
COPY dameon/configuration.py ./configuration.py
COPY dameon/models.py ./models.py
COPY dameon/adminDecorater.py ./adminDecorater.py
COPY dameon/requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

ENTRYPOINT ["python", "./application.py"]
