FROM debian:bookworm
MAINTAINER Tim Molteno "tim@elec.ac.nz"
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
    python3-healpy 

RUN apt-get install -y libhdf5-dev python3-pkgconfig

RUN rm -rf /var/lib/apt/lists/*

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv --system-site-packages $VIRTUAL_ENV
RUN sh /opt/venv/bin/activate
RUN /opt/venv/bin/pip install -U pip setuptools wheel
RUN /opt/venv/bin/pip install tart 
RUN /opt/venv/bin/pip install tart_tools 

ENV CONFIG_DIR=/config_data

COPY ./python_code /python_code
WORKDIR /python_code/tart_hardware_interface
RUN /opt/venv/bin/pip install .

WORKDIR /python_code/tart_web_api
RUN /opt/venv/bin/pip install .

COPY ./config_data /config_data
WORKDIR /app
ENV FLASK_APP=tart_web_api.main
#ENV FLASK_DEBUG=1
RUN /opt/venv/bin/pip install waitress

EXPOSE 5000
CMD ["/opt/venv/bin/waitress-serve", "--threads=1", "--port=5000", "tart_web_api:app.app"]
