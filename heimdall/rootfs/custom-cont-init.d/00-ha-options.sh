#!/usr/bin/with-contenv bash
# shellcheck shell=bash

set -o pipefail

OPTIONS_FILE="/data/options.json"
S6_ENV_DIR="/run/s6/container_environment"

if [ ! -f "${OPTIONS_FILE}" ]; then
    echo "[ha-options] ${OPTIONS_FILE} not found, skipping"
    exit 0
fi

mkdir -p "${S6_ENV_DIR}"

TZ_VALUE="$(jq -r '.timezone // empty' "${OPTIONS_FILE}")"

if [ -z "${TZ_VALUE}" ] && [ -n "${SUPERVISOR_TOKEN:-}" ]; then
    if SUPERVISOR_TZ="$(curl -fsS --max-time 5 \
        -H "Authorization: Bearer ${SUPERVISOR_TOKEN}" \
        "http://supervisor/info" | jq -r '.data.timezone // empty')"; then
        TZ_VALUE="${SUPERVISOR_TZ}"
    else
        echo "[ha-options] Unable to read timezone from Supervisor, keeping image default"
    fi
fi

if [ -n "${TZ_VALUE}" ] && [ -f "/usr/share/zoneinfo/${TZ_VALUE}" ]; then
    printf '%s' "${TZ_VALUE}" > "${S6_ENV_DIR}/TZ"
    ln -snf "/usr/share/zoneinfo/${TZ_VALUE}" /etc/localtime
    echo "[ha-options] Timezone set to ${TZ_VALUE}"
elif [ -n "${TZ_VALUE}" ]; then
    echo "[ha-options] Unknown timezone '${TZ_VALUE}', keeping image default"
fi

if jq -e '.allow_internal_requests == true' "${OPTIONS_FILE}" >/dev/null 2>&1; then
    printf '%s' "true" > "${S6_ENV_DIR}/ALLOW_INTERNAL_REQUESTS"
    echo "[ha-options] ALLOW_INTERNAL_REQUESTS=true"
else
    printf '%s' "false" > "${S6_ENV_DIR}/ALLOW_INTERNAL_REQUESTS"
fi

exit 0
