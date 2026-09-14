#!/usr/bin/with-contenv bashio
# shellcheck shell=bash

bashio::log.info "Starting 延时摄影 (HTTP Timelapse)..."

if bashio::config.has_value 'timezone'; then
    bashio::log.info "Timezone: $(bashio::config 'timezone')"
fi

exec python3 /main.py
