#!/usr/bin/with-contenv bashio
# shellcheck shell=bash

bashio::log.info "Starting HTTP Timelapse app..."

directory="$(bashio::config 'directory')"
bashio::log.info "Serving timelapse media from ${directory}"

exec python3 /server.py "${directory}"
