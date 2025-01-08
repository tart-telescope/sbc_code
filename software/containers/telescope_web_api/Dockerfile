FROM debian:bookworm
LABEL Maintainer: Tim Molteno "tim@elec.ac.nz"
ARG DEBIAN_FRONTEND=noninteractive

# debian setup
RUN apt-get update -y && apt-get install -y \
    curl \
    python3-python-flask-jwt-extended \
    python3-pip \
    python3-venv \
    python3-requests \
    python3-dateutil \
    python3-matplotlib \
    python3-yaml \
    python3-psycopg2 \
    python3-jsonrpclib-pelix \
    python3-h5py \
    python3-astropy \
    python3-healpy \
    python3-pycryptodome \
    python3-argon2 \
    python3-tqdm

RUN apt-get install -y libhdf5-dev python3-pkgconfig cython3

RUN rm -rf /var/lib/apt/lists/*

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv --system-site-packages $VIRTUAL_ENV

# All the following are to avoid a stupid debian bug which builds h5py 
# and this takes hours on an RPi (it can't use system-site-packages)
# Also fails on 3.11. TODO H5PY fix (when h5py has wheels on aarch64, this will be fine)
# RUN . /opt/venv/bin/activate && pip3 install  "h5py<=3.10"
RUN . /opt/venv/bin/activate && pip3 install --no-deps tart  # --no-deps to avoid depending on h5py
RUN . /opt/venv/bin/activate && pip3 install "minio<=7.1"
RUN . /opt/venv/bin/activate && pip3 install --no-deps tart_tools   # --no-deps to avoid depending on h5py

ENV CONFIG_DIR=/config_data

COPY ./python_code /python_code
WORKDIR /python_code/tart_hardware_interface
RUN . /opt/venv/bin/activate && pip3 install   .

WORKDIR /python_code/tart_web_api
RUN . /opt/venv/bin/activate && pip3 install  .

COPY ./config_data /config_data
WORKDIR /app
ENV FLASK_APP=tart_web_api.app
#ENV FLASK_DEBUG=1
RUN . /opt/venv/bin/activate && pip3 install waitress

EXPOSE 5000
CMD ["/opt/venv/bin/waitress-serve", "--threads=1", "--port=5000", "tart_web_api.app:app"]
