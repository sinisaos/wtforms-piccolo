#!/bin/bash

echo "Running flake8..."
flake8 .
echo "-----"

echo "Running isort..."
isort .
echo "-----"

echo "Running black..."
black .

echo "Running mypy..."
mypy .
