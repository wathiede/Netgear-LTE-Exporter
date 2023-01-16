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
        self.data_usage = Gauge("netgear_lte_data_usage", "Data Usage")

        self.spn_info = Info("netgear_lte_spn_info", "Information on SPN")
        self.modem_info = Info("netgear_lte_modem_info", "Information on the modem")


        self.wwan_info = Info("netgear_lte_wwan_info", "Connection information")
        self.wwan_sessDuration = Gauge("netgear_lte_wwan_sess_duration", "Session Duration")
        self.wwan_sessStartTime = Gauge("netgear_lte_sess_start_time", "Session Start Time")
        self.wwan_dataTransferred_total = Gauge("netgear_lte_data_total", "Data transferred total")
        self.wwan_dataTransferred_rxb = Gauge("netgear_lte_data_rxb", "Data transferred rxb")
        self.wwan_dataTransferred_txb = Gauge("netgear_lte_data_txb", "Data transferred txb")


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
            self.data_usage.set(result.usage)

            # self.spn_info.info({'spn_name':})
            self.modem_info.info({
                'model':result.items['general.model'],
                'fw_version':result.items['general.fwversion'],
                'app_version':result.items['general.appversion'],
                'network_display':result.items['wwan.registernetworkdisplay']
            })

            self.wwan_info.info({
                'connection_text':result.items['wwan.connectiontext'],
                'curBand':result.items['wwanadv.curband']
            })
            self.wwan_sessDuration.set(result.items['wwan.sessduration'])
            self.wwan_sessStartTime.set(result.items['wwan.sessstarttime'])
            self.wwan_dataTransferred_total.set(result.items['wwan.datatransferred.totalb'])
            self.wwan_dataTransferred_rxb.set(result.items['wwan.datatransferred.rxb'])
            self.wwan_dataTransferred_txb.set(result.items['wwan.datatransferred.txb'])


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