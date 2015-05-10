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
# to a file
./git_log_converter.py --repo /path/to/repo repo.json-dump

# to stdout
./git_log_converter.py --repo /path/to/repo -
```

For all options, use `./git_log_converter.py -h`.

Contributing
------------

```
virtualenv --python=python3 venv
source venv/bin/activate
pip install -r requirements.txt
flake8 (find . -name '*.py' | grep -v 'venv')
# hack away
```
