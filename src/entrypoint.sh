#!/bin/bash

flask db migrate
flask db upgrade

python3 -u run.py