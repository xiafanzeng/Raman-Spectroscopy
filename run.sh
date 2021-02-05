#!/bin/bash

if [ -d ".venv" ]
then
    source .venv/bin/activate
    pip install -r requirements.txt
    py wsgi.py
else
    py -m venv .venv
    source .venv/bin/activate
    py -m pip install --upgrade pip
    pip install -r requirements.txt
    py wsgi.py
fi
