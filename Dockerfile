FROM python:2.7

# based on https://github.com/pfichtner/docker-mqttwarn

# install mqttwarn
RUN pip install mqttwarn

# build /opt/mqttwarn
RUN mkdir -p /opt/mqttwarn
WORKDIR /opt/mqttwarn

# add user mqttwarn to image
RUN groupadd -r mqttwarn && useradd -r -g mqttwarn mqttwarn
RUN chown -R mqttwarn /opt/mqttwarn

# process run as mqttwarn user
USER mqttwarn

# conf file from host
VOLUME ["/opt/mqttwarn/conf"]

# set conf path
ENV MQTTWARNINI="/opt/mqttwarn/conf/mqttwarn.ini"

# run process
CMD mqttwarn

