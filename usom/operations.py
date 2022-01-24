from connectors.core.connector import Connector, ConnectorError, get_logger
import requests
import json
import xmltodict
import datetime
import os.path
import publicsuffix2
import re
import dateutil.parser
import validators

TMP_FILE = '/tmp/usom.cache.json'
logger = get_logger('usom')


def update(config):
    try:
        url = config.get("url")
        verify = config.get("verify")
        now = datetime.datetime.now()
        if os.path.exists(TMP_FILE):
            f = open(TMP_FILE)
            content = json.load(f)
            f.close()
            old = dateutil.parser.isoparse(content['date'])
            if (now - old) < datetime.timedelta(hours=config["expire_hours"]):
                return False
        try:
            response = requests.get(url, verify=verify)
            content = xmltodict.parse(response.text)
            content = content['usom-data']['url-list']
            content['date'] = now.isoformat()
            out_file = open(TMP_FILE, "w")
            json.dump(content, out_file, indent=6)
            out_file.close()
            return True
        except requests.exceptions.RequestException as ex:
            if response.status_code != 200:
                logger.error(f"USOM returned bad status code: {response.status_code}")
        return False
    except Exception as e:
        logger.exception("An exception occurred {0}".format(e))
        raise ConnectorError("{0}".format(e))


def lookup(config, params):
    update(config)
    try:
        url = params["url"].strip().lower()
        url = re.sub("https?://", "", url)
        path = url
        fqdn = url.split("/")[0]
        domain = ""
        if not validators.ipv4(url):
            domain = publicsuffix2.get_sld(fqdn)
        f = open(TMP_FILE)
        content = json.load(f)
        f.close()
        content = content['url-info']
        found = [d for d in content if
                 (domain == d['url'].lower() or path == d['url'].lower() or fqdn == d['url'].lower())]

        if len(found) > 0:
            f = {"found": True}
            f.update(found[0])
            return f
        else:
            return {"found": False}
    except Exception as e:
        logger.exception("An exception occurred {0}".format(e))
        raise ConnectorError("{0}".format(e))


def _check_health(config):
    try:
        return lookup(config, {"url": "8.8.8.8"}) == {"found": False}
    except Exception as e:
        raise ConnectorError("Unable to connect USOM {0}".format(e))
