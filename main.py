"""Application exporter"""

import os
import time
from prometheus_client import start_http_server, Gauge, Enum, Info
# import requests

import asyncio
import aiohttp
import eternalegypt

from dotenv import load_dotenv

load_dotenv()

class NetgearLTEMetrics:
    """
    Representation of Prometheus metrics and loop to fetch and transform
    application metrics into Prometheus metrics.
    """

    def __init__(self, app_port=80, polling_interval_seconds=5 ):
        self.app_port = app_port
        self.polling_interval_seconds = polling_interval_seconds

        #Netgear LTE
        self.rx_level = Gauge("netgear_lte_rx_level", "RX Level")
        self.tx_level = Gauge("netgear_lte_tx_level", "TX Level")
        self.radio_quality = Gauge("netgear_lte_radio_quality", "Radio Quality")
        self.usage = Gauge("netgear_lte_usage", "Usage")

        # Prometheus metrics to collect
        self.current_requests = Gauge("app_requests_current", "Current requests")
        self.pending_requests = Gauge("app_requests_pending", "Pending requests")

        self.app_version = Info("app_version", "Firmware version")
        self.serial = Info("serial", "Serial Number")
        self.data_usage = Gauge("data_usage", "Data usage")

        self.total_uptime = Gauge("app_uptime", "Uptime")
        self.health = Enum("app_health", "Health", states=["healthy", "unhealthy"])

    def run_metrics_loop(self):
        """Metrics fetching loop"""

        while True:
            asyncio.get_event_loop().run_until_complete(self.fetch())
            time.sleep(self.polling_interval_seconds)

    async def fetch(self):
        """
        Get metrics from application and refresh Prometheus metrics with
        new values.
        """

        jar = aiohttp.CookieJar(unsafe=True)
        websession = aiohttp.ClientSession(cookie_jar=jar)

        try:
            modem = eternalegypt.Modem(hostname=os.getenv("MODEM_HOST"), websession=websession)
            await modem.login(password=os.getenv("MODEM_PASS"))
            result = await modem.information()

            await websession.close()

            self.rx_level.set(result.rx_level)
            self.tx_level.set(result.tx_level)
            self.radio_quality.set(result.radio_quality)
            self.usage.set(result.usage)

            # Update Prometheus metrics with application metrics
            self.data_usage.set(result.usage)
            self.serial.info({"number":result.serial_number})
            self.current_requests.set(2)
            self.pending_requests.set(3)
            self.total_uptime.set(1111)
            self.health.state("healthy")

            
            await modem.logout()
        except eternalegypt.Error:
            print("Could not login")

        await websession.close()


def main():
    """Main entry point"""

    polling_interval_seconds = int(os.getenv("POLLING_INTERVAL_SECONDS", "10"))
    app_port = int(os.getenv("APP_PORT", "80"))
    exporter_port = int(os.getenv("EXPORTER_PORT", "9877"))

    app_metrics = NetgearLTEMetrics(
        app_port=app_port,
        polling_interval_seconds=polling_interval_seconds
    )
    start_http_server(exporter_port)
    app_metrics.run_metrics_loop()

if __name__ == "__main__":
    main()