import logging
import requests
import json
import xmltodict
import datetime
import os.path
import publicsuffix2
import socket
import re
import dateutil.parser

# operations.py
from connectors.core.connector import Connector, get_logger

logger = get_logger('usom')


def update(config):
    url = config.get("url")
    verify = config.get("verify")
    now = datetime.datetime.now()
    if os.path.exists('/tmp/usom.cache.json'):
        f = open('/tmp/usom.cache.json')
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
        out_file = open("/tmp/usom.cache.json", "w")
        json.dump(content, out_file, indent=6)
        out_file.close()
        return True
    except requests.exceptions.RequestException as ex:
        if response.status_code != 200:
            logger.error(f"USOM returned bad status code: {response.status_code}")
    return False


def query(config, params):
    update(config)
    url = params["url"].strip().lower()
    url = re.sub("https?://", "", url)
    path = url
    fqdn = url.split("/")[0]
    domain = ""
    try:
        socket.inet_aton(url)
    except socket.error:
        domain = publicsuffix2.get_sld(fqdn)

    f = open('/tmp/usom.cache.json')
    content = json.load(f)
    f.close()
    content = content['url-info']
    found = [d for d in content if (domain == d['url'].lower() or path == d['url'].lower() or fqdn == d['url'].lower())]
    if len(found) > 0:
        f = {"found": True}
        f.update(found[0])
        return f
    else:
        return {"found": False}


def _check_health(config):
    try:
        return query(config, {"url": "8.8.8.8"}) == {"found": False}
    except Exception as e:
        raise Exception("Unable to connect USOM {0}".format(e))
