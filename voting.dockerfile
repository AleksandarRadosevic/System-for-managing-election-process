FROM python:3

RUN mkdir -p /opt/src/voting
WORKDIR /opt/src/voting

COPY voting/application.py ./application.py
COPY voting/configuration.py ./configuration.py
COPY voting/models.py ./models.py
COPY voting/roleDecorater.py ./roleDecorater.py
COPY voting/requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

ENTRYPOINT ["python", "./application.py"]
