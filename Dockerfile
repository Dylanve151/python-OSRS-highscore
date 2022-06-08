FROM debian
ENV db_host 127.0.0.1
ENV db_database osrsHighscore
ENV db_user osrsHighscore
ENV db_password password
ENV osrs_players "Zezima" "Torvesta"
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
COPY config.py /scripts/config.py
COPY osrsHighscore.py /scripts/osrsHighscore.py
COPY osrshc.bash /etc/cron.hourly/osrshc.bash
COPY startup .
RUN chmod 775 /etc/cron.hourly/* && \
  chmod 775 /startup
RUN mkdir /config
RUN rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
CMD [ "/startup" ]
