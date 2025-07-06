FROM debian:bookworm
LABEL Maintainer: Tim Molteno "tim@elec.ac.nz"
ARG DEBIAN_FRONTEND=noninteractive

# debian setup
RUN apt-get update -y && apt-get install -y \
    python3-pip \
    python3-venv

RUN rm -rf /var/lib/apt/lists/*

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV

# All the following are to avoid a stupid debian bug which builds h5py
# and this takes hours on an RPi (it can't use system-site-packages)
# Also fails on 3.11. TODO H5PY fix (when h5py has wheels on aarch64, this will be fine)
# RUN . /opt/venv/bin/activate && pip3 install  "h5py<=3.10"
RUN . /opt/venv/bin/activate && pip3 install --no-cache-dir tart  # --no-deps to avoid depending on h5py
# RUN . /opt/venv/bin/activate && pip3 install --no-cache-dir "minio<=7.1"
RUN . /opt/venv/bin/activate && pip3 install --no-cache-dir tart_tools   # --no-deps to avoid depending on h5py

ENV CONFIG_DIR=/config_data

COPY ./python_code /python_code
WORKDIR /python_code/tart_hardware_interface
RUN . /opt/venv/bin/activate && pip3 install --no-cache-dir .

WORKDIR /python_code/tart_web_api
RUN . /opt/venv/bin/activate && pip3 install --no-cache-dir .

ENV PERMUTE_DIR=/permute
COPY ./config_data/permute.txt /permute/permute.txt
WORKDIR /app
ENV FLASK_APP=tart_web_api.app
#ENV FLASK_DEBUG=1
RUN . /opt/venv/bin/activate && pip3 install --no-cache-dir waitress

EXPOSE 5000
CMD ["/opt/venv/bin/waitress-serve", "--threads=1", "--port=5000", "tart_web_api.app:app"]
