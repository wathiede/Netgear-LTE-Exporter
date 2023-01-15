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

        #NetgearLTE
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

        # Fetch raw status data from the application
        # resp = requests.get(url=f"http://localhost:{self.app_port}/status")
        # status_data = resp.json()

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

# async def get_information():
#     """Example of printing the current upstream."""
#     jar = aiohttp.CookieJar(unsafe=True)
#     websession = aiohttp.ClientSession(cookie_jar=jar)

#     try:
#         modem = eternalegypt.Modem(hostname=os.getenv("MODEM_HOST"), websession=websession)
#         await modem.login(password=os.getenv("MODEM_PASS"))

#         result = await modem.information()
#         # if len(sys.argv) == 3:
#         print("serial_number: {}".format(result.serial_number))
#         print("usage: {}".format(result.usage))
#         print("upstream: {}".format(result.upstream))
#         print("wire_connected: {}".format(result.wire_connected))
#         print("mobile_connected: {}".format(result.mobile_connected))
#         print("connection_text: {}".format(result.connection_text))
#         print("connection_type: {}".format(result.connection_type))
#         print("current_nw_service_type: {}".format(result.current_nw_service_type))
#         print("current_ps_service_type: {}".format(result.current_ps_service_type))
#         print("register_network_display: {}".format(result.register_network_display))
#         print("roaming: {}".format(result.roaming))
#         print("radio_quality: {}".format(result.radio_quality))
#         print("rx_level: {}".format(result.rx_level))
#         print("tx_level: {}".format(result.tx_level))
#         print("current_band: {}".format(result.current_band))
#         print("cell_id: {}".format(result.cell_id))
#         # else:
#         #     key = sys.argv[3]
#         #     print("{}: {}".format(key, result.items.get(key)))

#         await modem.logout()
#     except eternalegypt.Error:
#         print("Could not login")

#     await websession.close()

# async def debugStuff():
#     jar = aiohttp.CookieJar(unsafe=True)
#     websession = aiohttp.ClientSession(cookie_jar=jar)

#     modem = eternalegypt.Modem(hostname="xxx", websession=websession)
#     await modem.login(password="xxx")
#     await modem.delete_sms(sms_id=0)
#     await modem.delete_sms(sms_id=1)
#     await modem.delete_sms(sms_id=2)
#     await modem.sms(message="Thisisatest",phone="xxx")
#     await modem.logout()



# @autologin
# async def information(self):
#     """Return the current information."""
#     url = self._url('model.json')
#     async with self.websession.get(url) as response:
#         data = json.loads(await response.text())

#         try:
#             result = self._build_information(data)
#             _LOGGER.debug("Did read information: %s", data)
#         except KeyError as ex:
#             _LOGGER.debug("Failed to read information (%s): %s", ex, data)
#             raise Error()

#         self._sms_events(result)

#         return result

#     data['sms']['unreadMsgs']
#     data['sms']['msgCount']
#     data['general']['appVersion']

#     result.serial_number
#     result.usage
#     result.upstream
#     result.wire_connected
#     result.mobile_connected
#     result.connection_text
#     result.connection_type
#     result.current_nw_service_type
#     result.current_ps_service_type
#     result.register_network_display
#     result.roaming
#     result.radio_quality
#     result.rx_level
#     result.tx_level
#     result.current_band
#     result.cell_id

# async def login():
#     jar = aiohttp.CookieJar(unsafe=True)
#     websession = aiohttp.ClientSession(cookie_jar=jar)

#     modem = eternalegypt.Modem(hostname="xxx", websession=websession)
#     await modem.login(password="xxx")


#     await websession.close()
#     return modem

def main():
    """Main entry point"""

    polling_interval_seconds = int(os.getenv("POLLING_INTERVAL_SECONDS", "10"))
    app_port = int(os.getenv("APP_PORT", "80"))
    exporter_port = int(os.getenv("EXPORTER_PORT", "9877"))

    # asyncio.get_event_loop().run_until_complete(get_information())
    
    # modem = asyncio.get_event_loop().run_until_complete(login())

    # asyncio.get_event_loop().run_until_complete(debugStuff())
    
    # while(True):
    #     asyncio.get_event_loop().run_until_complete(get_information())
    #     time.sleep(2)

    app_metrics = NetgearLTEMetrics(
        app_port=app_port,
        polling_interval_seconds=polling_interval_seconds
    )
    start_http_server(exporter_port)
    app_metrics.run_metrics_loop()

if __name__ == "__main__":
    main()