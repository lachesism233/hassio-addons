ARG BUILD_FROM
FROM ${BUILD_FROM}

COPY rootfs/ /

RUN chmod +x /custom-cont-init.d/00-ha-options.sh
