FROM python:3.13-bookworm AS builder
LABEL Maintainer: Tim Molteno "tim@elec.ac.nz"
ARG DEBIAN_FRONTEND=noninteractive
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV

COPY ./python_code /python_code
RUN . /opt/venv/bin/activate && pip3 install --no-cache-dir /python_code/tart_hardware_interface
RUN . /opt/venv/bin/activate && pip3 install --no-cache-dir /python_code/tart_web_api
# RUN . /opt/venv/bin/activate && pip3 install --no-cache-dir tart>=1.3.1 # --no-deps to avoid depending on h5py

RUN . /opt/venv/bin/activate && pip3 install --no-cache-dir waitress scipy requests

FROM python:3.13-slim-bookworm AS runtime

ENV PYTHONUNBUFFERED=1
ARG SECRET_KEY
ENV SECRET_KEY=$SECRET_KEY
ENV VIRTUAL_ENV=/opt/venv
ENV CONFIG_DIR=/config_data
ENV PERMUTE_DIR=/permute
COPY ./config_data/permute.txt /permute/permute.txt

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv

EXPOSE 5000
CMD ["/opt/venv/bin/waitress-serve", "--threads=1", "--port=5000", "tart_web_api.app:app"]
