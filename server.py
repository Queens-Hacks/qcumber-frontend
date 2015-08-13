#!/usr/bin/env python
"""
Runs the Qcumber frontend server in development mode
"""

from qcumber import APP

try:
    from qcumber import config
except ImportError:
    from qcumber import default_config as config

if __name__ == '__main__':
    APP.run(port=config.port, debug=config.DEBUG)
