Git Log Converter
=================

Converts your Git repository log into lines of JSON.

Prerequisites
-------------

 - libgit2
 - python3

Usage
-----

```
./git_log_converter.py --repo /path/to/repo
```

That will write to stdout, which can be easily redirected to a file.

Alternatively, this can be combined with `json_log_to_db.py` to write to a database.
Before writing to a database, you'll need to have a driver like psycopg2 installed.

```
./git_log_converter.py --repo /path/to/repo | ./json_log_to_db.py --connection-string <conn_string> -
```

For all options, use `./git_log_converter.py -h` and `./json_log_to_db.py -h`.

Contributing
------------

```
virtualenv --python=python3 venv
source venv/bin/activate
pip install -r requirements.txt
flake8 (find . -name '*.py' | grep -v 'venv')
# hack away
```
