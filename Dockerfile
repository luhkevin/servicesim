FROM python:2-alpine

MAINTAINER netsil

RUN apk update && apk upgrade && apk add openssl openssl-dev musl-dev gcc libffi libffi-dev && pip2 install klein treq

RUN apk add bash wget unzip

COPY . /opt/servicesim
#RUN mkdir -p /opt/servicesim && wget --no-check-certificate https://github.com/luhkevin/servicesim/archive/master.zip -O /opt/servicesim/servicesim.zip
#RUN unzip /opt/servicesim/servicesim.zip -d /opt/servicesim

EXPOSE 8000-8050
EXPOSE 8080

ENTRYPOINT ["python", "/opt/servicesim/simserver.py"]
CMD ["-a", "0.0.0.0", "-n", "A", "-p", "8000"]
