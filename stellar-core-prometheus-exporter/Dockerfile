FROM ubuntu:16.04
RUN apt-get update && apt-get install -y gnupg2 wget apt-utils apt-transport-https
RUN wget -qO - https://apt.stellar.org/SDF.asc | apt-key add - && \
    echo "deb https://apt.stellar.org/public stable/" | tee -a /etc/apt/sources.list.d/SDF.list
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y stellar-core-prometheus-exporter

CMD /usr/bin/stellar-core-prometheus-exporter.py
