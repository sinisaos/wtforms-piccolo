#!/bin/bash

python -m pytest tests/test_table_form.py --cov=wtforms_piccolo --cov-report xml --cov-report html --cov-fail-under 90 -s $@
