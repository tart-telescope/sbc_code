# Build our own headscale distribution

FROM docker.io/golang:1.22-bookworm AS build
ARG VERSION=0.22.3
ENV GOPATH /go
WORKDIR /go/src

RUN git clone --depth 1 --branch "v$VERSION" https://github.com/juanfont/headscale.git
WORKDIR /go/src/headscale

RUN go mod download

RUN CGO_ENABLED=0 GOOS=linux go install -ldflags="-s -w -X github.com/juanfont/headscale/cmd/headscale/cli.Version=$VERSION" -a ./cmd/headscale
RUN test -e /go/bin/headscale

# Debug image
FROM docker.io/golang:1.22-bookworm

COPY --from=build /go/bin/headscale /bin/headscale
ENV TZ UTC

RUN apt-get update \
  && apt-get install --no-install-recommends --yes less jq \
  && rm -rf /var/lib/apt/lists/* \
  && apt-get clean
RUN mkdir -p /var/run/headscale

# Need to reset the entrypoint or everything will run as a busybox script
ENTRYPOINT []
EXPOSE 8080/tcp
CMD ["headscale"]
