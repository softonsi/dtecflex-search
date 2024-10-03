# Guia

Instalação e Configuração do ambiente

## Instalação

Instale o Python 3.12 usando o pyenv:

```bash
pyenv install 3.12
```

Defina o Python 3.12 como a versão global:

```bash
pyenv global 3.12
```

Crie um ambiente virtual com o uv:

```bash
uv venv
```

Ative o ambiente virtual:

```bash
source .venv/bin/activate
```

Sincronize as dependências do projeto:

```bash
uv sync
```
