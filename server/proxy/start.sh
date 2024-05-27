#!/bin/sh
/app/tailscaled --state=/var/lib/tailscale/tailscaled.state --socket=/var/run/tailscale/tailscaled.sock &
/app/tailscale up --hostname=${TS_HOSTNAME} --accept-dns=${TS_ACCEPT_DNS} --authkey=${TS_AUTHKEY} ${TS_EXTRA_ARGS} 
which nginx
nginx -g 'pid /tmp/nginx.pid; daemon off;'
