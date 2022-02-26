from connectors.core.connector import Connector, ConnectorError, get_logger
import requests
from urllib.parse import urlparse
import xmltodict

logger = get_logger('usom')


def get_feed(config, params):
    try:
        url = config.get("url")
        verify = config.get("verify")
        response = requests.get(url, verify=verify)
        content = xmltodict.parse(response.text)
        return content
    except Exception as e:
        logger.exception("An exception occurred {0}".format(e))
        raise ConnectorError("{0}".format(e))


def _check_health(config):
    try:
        url = config.get("url")
        verify = config.get("verify")
        domain = urlparse(url).netloc
        protocol = "https://" if verify else "http://"
        response = requests.get(f"{protocol}{domain}", verify=verify)
        if response.status_code != 200:
            raise ConnectorError("Unable to connect USOM")
        return True
    except Exception as e:
        raise ConnectorError("Unable to connect USOM {0}".format(e))
