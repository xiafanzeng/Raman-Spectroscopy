#!/bin/bash

if [ -d ".venv" ]
then
    source .venv/bin/activate
    #pip install -r requirements.txt
    python3 wsgi.py
else
    python3 -m venv .venv
    source .venv/bin/activate
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    python wsgi.py
fi