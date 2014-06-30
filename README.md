# Qcumber Frontend
Note: If you're looking for the easy to use course catalog for Queen's University, you came close! This is the code for the frontend interface that powers it. You'll want to head to https://qcumber.ca for the end user site :).

This is a simple flask application which talks to [Elasticsearch](http://www.elasticsearch.org/) as a data store, and consumes the data found in [qcumber-data](https://github.com/Queens-Hacks/qcumber-data).

## Setup
Currently, the frontend is in a bit of a messy state, as it was thrown together over the course of a week to get it ready in time for course selection.

Clone this repository
```bash
$ git clone https://github.com/Queens-Hacks/qcumber-frontend
```

Create a [virtualenv](https://pypi.python.org/pypi/virtualenv) and install the requirements from the requirements.txt file into it.
```bash
$ virtualenv env
$ . env/bin/activate
$ pip install -r requirements.txt
```

Install `elasticsearch` and get it running. Currently the code only supports the default ports, but there will be options to configure that soon.

Clone the data repository into the `out` directory.
```bash
$ git clone https://github.com/Queens-Hacks/qcumber-data out
```

Run the `fill.py` script to load the data into the elasticsearch instance.
```bash
$ ./fill.py
```

Now the debug server can be run by running `main.py`
```bash
$ ./main.py
```

