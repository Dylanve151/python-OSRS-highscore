FROM debian
RUN apt-get update && apt-get install -y \
  cron \
  python3 \
  python3-pip \
  && apt-get clean
RUN echo '0 */1 * * * root /etc/cron.hourly/* > /proc/1/fd/1 2>/proc/1/fd/2' >> /etc/crontab
RUN python3 -m pip install \
  bs4 \
  datetime \
  requests \
  configparser \
  psycopg2-binary
VOLUME ["/etc/cron.hourly"]
VOLUME ["/scripts"]
VOLUME ["/config"]
RUN rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
CMD [ "cron -f" ]
