Netgear LTE Modem Exporter
===


# Tested Devices

* Netgear LM1200

# Config Example

## Docker CLI

    docker run -d --name lte-exporter \
        -p 9877:9877 \
        -e MODEM_HOST=192.168.5.1 \
        -e MODEM_PASS=redtable654 \
        ghcr.io/ncareau/netgear-lte-exporter:latest

## Docker Compose

    lte-exporter:
        image: ghcr.io/ncareau/netgear-lte-exporter:latest
        container_name: lte-exporter
        environment:
            - MODEM_HOST=192.168.5.1
            - MODEM_PASS=redtable654
        ports:
            - 9877:9877
        restart: unless-stopped


# Thanks 

* https://github.com/amelchio/eternalegypt
* https://github.com/ickymettle/netgear_cm_exporter
