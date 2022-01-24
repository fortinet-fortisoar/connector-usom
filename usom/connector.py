from connectors.core.connector import Connector, ConnectorError, get_logger
from .operations import lookup, _check_health

logger = get_logger('usom')


class Usom(Connector):
    def execute(self, config, operation_name, params, **kwargs):
        logger.info("operation_name: {0}".format(operation_name))
        operations = {
            'lookup': lookup
        }
        action = operations.get(operation_name)
        return action(config, params)

    def check_health(self, config):
        try:
            return _check_health(config)
        except Exception as e:
            raise ConnectorError(e)

# def test():
#     config = {"token": "9IBS09sfQuq1NzzCeWaEBA=="}
#     params = {"ip": "8.8.8.8"}
#     KasperskyThreatLookupAPI().execute(config, "lookup_ip", params)
