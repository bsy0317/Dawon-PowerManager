#!/bin/bash
gunicorn -c gunicorn.conf.py dawon_pm:app