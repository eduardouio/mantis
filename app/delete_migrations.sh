#!/bin/bash


BASE_DIR=$(pwd)


find "$BASE_DIR" -path "*/migrations/*.py" ! -name "__init__.py" -delete


find "$BASE_DIR" -path "*/migrations/*.pyc" -delete

echo "Carpetas de migrations eliminadas."
