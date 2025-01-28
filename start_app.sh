#!/bin/bash

# Obtém o diretório do script

DIR="$(dirname "$(readlink -f "$0")")"
cd $DIR

UV=$(which uv)
DATA=$(date '+%Y-%m-%d_%H-%M-%S')
LOG="$DIR/log/app_$DATA.log"

echo "DIR: $(pwd)"
echo "LOG: $LOG"
echo "UV : $UV"

mkdir -p "$DIR/log"

# Redireciona toda a saída do script para o log
exec >> "$LOG" 2>&1

# $UV venv
source .venv/bin/activate

streamlit run app.py --server.port 8502

