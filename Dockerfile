FROM python:3.8.2-slim-buster

# based on https://github.com/pfichtner/docker-mqttwarn

# install mqttwarn
RUN pip install mqttwarn

# install extra dependencies needed for our services/functions
RUN pip install slacker gpxpy

# create /etc/mqttwarn
RUN mkdir -p /etc/mqttwarn
WORKDIR /etc/mqttwarn

# add user mqttwarn to image
RUN groupadd -r mqttwarn && useradd -r -g mqttwarn mqttwarn
RUN chown -R mqttwarn:mqttwarn /etc/mqttwarn

# process run as mqttwarn user
USER mqttwarn

# conf file from host
VOLUME ["/etc/mqttwarn"]

# set conf path
ENV MQTTWARNINI="/etc/mqttwarn/mqttwarn.ini"

# run process
CMD mqttwarn

