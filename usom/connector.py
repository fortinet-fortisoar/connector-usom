from connectors.core.connector import Connector, ConnectorError, get_logger

from .operations import *
from .operations import _check_health
##sudo -u nginx /opt/cyops-integrations/.env/bin/pip install -r /opt/cyops-integrations/integrations/connectors/usom_1_0_0/requirements.txt

logger = get_logger('usom')


class Usom(Connector):
    def execute(self, config, operation_name, params, **kwargs):
        # raise Exception(operation_name)
        try:
            logger.info("operation_name: {0}".format(operation_name))
            result = None
            if operation_name == 'lookup_url':
                result = query(config, params)
            return result
        except Exception as e:
            logger.exception("An exception occurred {0}".format(e))
            raise ConnectorError("{0}".format(e))

    def check_health(self, config):
        try:
            return _check_health(config)
        except Exception as e:
            raise ConnectorError(e)

# def test():
#     config = {"token": "9IBS09sfQuq1NzzCeWaEBA=="}
#     params = {"ip": "8.8.8.8"}
#     KasperskyThreatLookupAPI().execute(config, "lookup_ip", params)
