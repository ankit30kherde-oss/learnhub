# Disposable environment learners practice in. It is rebuilt/recreated per session.
FROM ubuntu:22.04

RUN apt-get update && apt-get install -y --no-install-recommends \
    bash ca-certificates curl wget git vim nano less jq htop tree \
    net-tools iproute2 iputils-ping dnsutils procps psmisc lsof \
    tar gzip unzip \
    && rm -rf /var/lib/apt/lists/*

RUN echo 'PS1="learner@sandbox:\\w\\$ "' >> /root/.bashrc

WORKDIR /root
CMD ["sleep", "infinity"]
