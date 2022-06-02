#!/bin/bash

SOURCES="wtforms_piccolo tests"

isort $SOURCES
black $SOURCES
flake8 $SOURCES
mypy $SOURCES
