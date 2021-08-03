FROM ubuntu:focal

LABEL name="biosaur_docker"
LABEL version="0.1"
LABEL docker_author="Michael A. Freitas"
LABEL docker_maintainer="mike.freitas@gmail.com"
LABEL dockerhub="mfreitas/biosaur"

RUN apt-get update -y  && DEBIAN_FRONTEND=noninteractive apt-get install \
    --fix-missing libgtk2.0-dev python3-pip procps -y && \
    rm -rf /var/lib/apt/lists/*

ADD ./Biosaur /build

RUN cd /build && \
    pip3 install -r requirements.txt && \
    pip3 install pyopenms && pip3 install . && \
    cd / && \
    rm -rf /build

ADD BiosaurAdapter.py /usr/local/bin/BiosaurAdapter






