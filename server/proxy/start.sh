#!/bin/sh
/app/tailscaled --state=/var/lib/tailscale/tailscaled.state --socket=/var/run/tailscale/tailscaled.sock &
/app/tailscale up # --authkey=${TAILSCALE_AUTHKEY}
which nginx
nginx -g 'pid /tmp/nginx.pid; daemon off;'
