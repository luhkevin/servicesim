FROM python:2-alpine

MAINTAINER netsil

RUN apk update && apk upgrade && apk add openssl openssl-dev musl-dev gcc libffi libffi-dev && pip2 install klein treq

RUN apk add bash wget unzip

COPY . /opt/servicesim

EXPOSE 8000-8050
EXPOSE 8080

CMD ["python", "/opt/servicesim/simserver.py", "-a", "0.0.0.0", "-n", "alpha", "-p", "8000"] 

