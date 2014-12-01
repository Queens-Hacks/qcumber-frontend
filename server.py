#!/usr/bin/env python
"""
Runs the Qcumber frontend server in development mode
"""

from qcumber import APP

# Run the debug server
if __name__ == '__main__':
    APP.run(port=3000, debug=True)
