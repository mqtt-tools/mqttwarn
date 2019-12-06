FROM python:2.7

# based on https://github.com/pfichtner/docker-mqttwarn

# install python libraries (TODO: any others?)
RUN pip install paho-mqtt requests jinja2 slacker

# build /opt/mqttwarn
RUN mkdir -p /opt/mqttwarn
RUN mkdir -p /home/mqttwarn
RUN mkdir -p /opt/local-services

WORKDIR /opt/mqttwarn

# add user mqttwarn to image
RUN groupadd -r mqttwarn && useradd -r -g mqttwarn mqttwarn
RUN chown -R mqttwarn /opt/mqttwarn
RUN chown -R mqttwarn /home/mqttwarn


# process run as mqttwarn user
USER mqttwarn

# conf file from host
VOLUME ["/opt/mqttwarn/conf"]

# set conf path
ENV MQTTWARNINI="/opt/mqttwarn/conf/mqttwarn.ini"

# finally, copy the current code (ideally we'd copy only what we need, but it
#  is not clear what that is, yet)
COPY . /opt/mqttwarn

# run process
CMD ["/bin/bash" , "run.sh"]


