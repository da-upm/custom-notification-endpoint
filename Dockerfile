FROM python:3.11

COPY requirements.txt /srv/requirements.txt
COPY main.py /srv/main.py

RUN pip3 install -r /srv/requirements.txt

EXPOSE 3000

ENTRYPOINT python3 /srv/main.py