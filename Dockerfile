FROM python:3.8.2-slim-buster

#install dir
RUN mkdir -p /app

# run dir
RUN mkdir -p /etc/mqttwarn/
WORKDIR /etc/mqttwarn

# conf file from host
VOLUME ["/etc/mqttwarn"]

# set conf path
ENV MQTTWARNINI="/etc/mqttwarn/mqttwarn.ini"

# copy and install requirements
COPY . /app
RUN cd /app && python setup.py develop

# run process
CMD mqttwarn

