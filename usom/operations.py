""" Copyright start
  Copyright (C) 2008 - 2022 Fortinet Inc.
  All rights reserved.
  FORTINET CONFIDENTIAL & FORTINET PROPRIETARY SOURCE CODE
  Copyright end """


from connectors.core.connector import Connector, ConnectorError, get_logger
import requests
from urllib.parse import urlparse
import xmltodict, datetime, time

logger = get_logger('usom')



def make_rest_call(config, method='GET'):
    try:
        server_url = config.get('server_url')
        response = requests.request(method, server_url, verify=config.get('verify'))
        if response.ok:
            return response
        else:
            logger.error(response.text)
            raise ConnectorError({'status_code': response.status_code, 'message': response.reason})
    except requests.exceptions.SSLError:
        raise ConnectorError('SSL certificate validation failed')
    except requests.exceptions.ConnectTimeout:
        raise ConnectorError('The request timed out while trying to connect to the server')
    except requests.exceptions.ReadTimeout:
        raise ConnectorError('The server did not send any data in the allotted amount of time')
    except requests.exceptions.ConnectionError:
        raise ConnectorError('Invalid endpoint or credentials')



def _check_health(config):
    try:
        url = config.get("server_url")
        verify = config.get("verify")
        domain = urlparse(url).netloc
        protocol = "https://" if verify else "http://"
        response = requests.get(f"{protocol}{domain}", verify=verify)
        if response.status_code != 200:
            raise ConnectorError("Unable to connect USOM")
        return True
    except Exception as err:
        logger.exception('{0}'.format(err))
        raise ConnectorError("Unable to connect USOM {0}".format(err))



def convert_datetime(last_pull_time):
    last_pull_timestamp = datetime.datetime.strptime(str(last_pull_time), "%Y-%m-%dT%H:%M:%S.%fZ").timestamp()
    return last_pull_timestamp


def check_duplicate_records(input_list):
    seen = set()
    final_result = [x for x in input_list if
                    [x['url'].replace(" ", "") not in seen, seen.add(x['url'].replace(" ", ""))][0]]
    return final_result


def get_feed(config, params):
    try:
        last_pull_time = params.get('modified_after')
        response = make_rest_call(config)
        content = xmltodict.parse(response.text)
        content = content["usom-data"]["url-list"]  # 2022-04-19 07:26:29.016155
        if last_pull_time:
            last_pull_timestamp = convert_datetime(last_pull_time)
            url_list = []
            for url_dict in content["url-info"]:
                dd = url_dict["date"]
                try:
                    create_date_timestamp = int(datetime.datetime.strptime(url_dict["date"], "%Y-%m-%d %H:%M:%S.%f").timestamp())
                except:
                    create_date_timestamp = int(datetime.datetime.strptime(url_dict["date"], "%Y-%m-%d %H:%M:%S").timestamp())
                if create_date_timestamp > last_pull_timestamp:
                    url_list.append(url_dict)
            return check_duplicate_records(url_list)
        else:
            return check_duplicate_records(content["url-info"])
    except Exception as e:
        logger.exception("An exception occurred {0}".format(e))
        raise ConnectorError("{0}".format(e))



operations = {
    'get_feed': get_feed
}
