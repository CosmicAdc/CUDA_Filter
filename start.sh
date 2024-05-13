#!/bin/bash
# Cambiar al directorio app y ejecutar poetry run uvicorn
cd /app/app && poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
# Iniciar ng serve en el directorio front_cuda
cd /app/front_cuda && ng serve --host 0.0.0.0


