""" Copyright start
  Copyright (C) 2008 - 2022 Fortinet Inc.
  All rights reserved.
  FORTINET CONFIDENTIAL & FORTINET PROPRIETARY SOURCE CODE
  Copyright end """


from connectors.core.connector import Connector, ConnectorError, get_logger
from .operations import get_feed, operations, _check_health

logger = get_logger('usom')


class Usom(Connector):
    def execute(self, config, operation_name, params, **kwargs):
      logger.info("operation_name: {0}".format(operation_name))
      action = operations.get(operation_name)
      return action(config, params)

    def check_health(self, config):
      return _check_health(config)
        
