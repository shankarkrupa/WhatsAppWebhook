#!/bin/bash
pip install --no-cache-dir -r /app/requirements.txt
exec uvicorn main:app --host 0.0.0.0 --port 80
