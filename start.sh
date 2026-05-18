#!/bin/bash
cd ~/tour-guide-ai/backend
export DASHSCOPE_API_KEY="sk-ef0fafd707114136911ea8b69be0fa2c"
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
