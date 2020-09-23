FROM python:latest

LABEL MAINTAINER="Fanis Triantafillis fanis_30fillis@outlook.com"

ENV GROUP_ID=1000 \
    USER_ID=1000

ADD ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
CMD ["mkdir", "app"]
ADD . .
EXPOSE 5000
CMD ["python","-u","app.py"]
