# Guia

A aplicação foi configurada para rodar em ambiente virtual com o `uv`.
## Requisitos

- Python 3.12
- uv

## Instalação

Instale o uv:

[https://docs.astral.sh/uv/getting-started/installation/#installation-methods](https://docs.astral.sh/uv/getting-started/installation/#installation-methods)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Baixe o projeto:

```bash
git clone https://github.com/sandro-fidelis/dtecflex-search.git
```
No diretório do projeto e ajuste o arquivo .env com as configurações do banco de dados:

```bash
cd dtecflex-search
cp .env.example .env
nano .env
```
```ini
DB_USER=
DB_PASS=
DB_PORT=
DB_HOST=
DB_NAME=
OPENAI_API_KEY=
SECRET_KEY=secret123
```

## Crie um ambiente virtual

Baseado no arquivo **pyproject.toml** o **uv** cria um ambiente virtual  e instala todas as dependências do projeto.

```bash
uv venv

Using CPython 3.12.0
Creating virtual environment at: .venv
Activate with: source .venv/bin/activate

```

Sincronize as dependências do projeto:

```bash
uv sync

Resolved 85 packages in 2.89s
Audited 83 packages in 0.05ms

```

## Execução

Use o script start_app.py para iniciar o servidor:

```bash
./start_app.py
```

## Configurar inicialização automática do servidor

Para configurar o servidor para iniciar automaticamente quando o computador é ligado, usando o `systemd`, siga as instruções abaixo:

```bash
# Crie o arquivo de serviço
sudo touch /etc/systemd/system/dtecflex-search.service

# Abra o arquivo em um editor de texto
sudo nano /etc/systemd/system/dtecflex-search.service
``` 

Adicione o seguinte conteúdo ao arquivo:

```ini
[Unit]
Description=DTEC-flex Search Platform
After=network.target

[Service]
User={USUARIO DO SERVIDOR}
WorkingDirectory={CAMINHO DO PROJETO}
ExecStart={CAMINHO DO PROJETO}/start_app.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target

Para habilitar o serviço, execute:

```bash
sudo systemctl enable dtecflex-search.service
``` 

Para iniciar o serviço, execute:

```bash
sudo service start dtecflex-search
``` 

Para verificar o status do serviço, execute:

```bash
sudo service status dtecflex-search
● dtecflex-search.service - DTEC-flex Search Platform
     Loaded: loaded (/etc/systemd/system/dtecflex-search.service; enabled; vendor preset: enabled)
     Active: active (running) since Fri 2025-01-24 11:05:32 -03; 4 days ago
   Main PID: 10758 (start_app.sh)
...
``` 

Se o status for `active (running)`, o servidor estará rodando.
Para reiniciar o serviço, execute:

```bash
sudo service restart dtecflex-search
``` 

Para parar o serviço, execute:

```bash
sudo service stop dtecflex-search
``` 
