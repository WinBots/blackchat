\
@echo off
set PYTHONPATH=%CD%
uvicorn app.main:app --host 0.0.0.0 --port 8061
