# Qcumber Frontend

Note: If you're looking for the easy to use course catalog for Queen's University, you came close!
This is the code for the frontend interface that powers it. You'll want to head to
https://qcumber.ca for the end user site :).

This is a simple flask application which servers the data found in
[qcumber-data](https://github.com/Queens-Hacks/qcumber-data).

## Setup

Clone this repository
```bash
git clone https://github.com/Queens-Hacks/qcumber-frontend
```

Create a [virtualenv](https://pypi.python.org/pypi/virtualenv) and install the requirements from
the requirements.txt file into it.
```bash
virtualenv env
. env/bin/activate
pip install -r requirements.txt
```

Create the database and load the data...
See [qcumber-db](https://github.com/Graham42/qcumber-db)

Now the debug server can be run by running `main.py`
```bash
$ ./main.py
```

