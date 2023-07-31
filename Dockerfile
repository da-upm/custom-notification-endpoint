FROM python:3.12

COPY requirements.txt /srv/requirements.txt
COPY main.py /srv/main.py

RUN pip3 install -r /srv/requirements.txt

ENTRYPOINT python3 /srv/main.py