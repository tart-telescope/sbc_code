FROM python:3.13-bookworm AS builder
LABEL Maintainer: Tim Molteno "tim@elec.ac.nz"

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV

COPY ./python_code/tart_hardware_interface /python_code/tart_hardware_interface
RUN --mount=type=cache,target=/root/.cache/pip \
    . /opt/venv/bin/activate && pip3 install /python_code/tart_hardware_interface
COPY ./python_code/tart_web_api /python_code/tart_web_api
RUN --mount=type=cache,target=/root/.cache/pip \
    . /opt/venv/bin/activate && pip3 install /python_code/tart_web_api
RUN --mount=type=cache,target=/root/.cache/pip \
    . /opt/venv/bin/activate && pip3 install waitress scipy requests

# RUN --mount=type=cache,target=/root/.cache/pip \
#     . /opt/venv/bin/activate && pip3 install tart>=1.3.1 # --no-deps to avoid depending on h5py

# delete all tests folders
RUN find /opt/venv/lib/python3.13/site-packages -name 'tests' -type d -exec rm -rf {} +
RUN find /opt/venv/lib/python3.13/site-packages -name '*dist-info' -type d -exec rm -rf {} +


FROM python:3.13-slim-bookworm AS runtime
ENV VIRTUAL_ENV=/opt/venv
ENV PYTHONUNBUFFERED=1

ARG SECRET_KEY
ENV SECRET_KEY=$SECRET_KEY
ARG LOGLEVEL=INFO
ENV LOGLEVEL=$LOGLEVEL
ENV CONFIG_DIR=/config_data
ENV PERMUTE_DIR=/permute
COPY ./config_data/permute.txt /permute/permute.txt

COPY --from=builder /opt/venv /opt/venv

EXPOSE 5000
CMD ["/opt/venv/bin/waitress-serve", "--threads=1", "--port=5000", "tart_web_api.app:app"]
