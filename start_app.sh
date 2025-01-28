#!/bin/bash

# Obtém o diretório do script
script_dir="$(dirname "$(readlink -f "$0")")"
cd $script_dir

echo "$script_dir"

mkdir -p ./log

/home/softon/.local/bin/uv venv
source .venv/bin/activate
$UV run streamlit run app.py --server.port 8502 >> "$LOG" 2>&1
