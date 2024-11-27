import concurrent.futures
import random
import subprocess
import time
from urllib.parse import unquote

import requests
from bs4 import BeautifulSoup


def extrair_texto_pagina(URL: str) -> str:
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'}
    response = requests.get(URL, headers=headers)
    # Faz a requisição HTTP para obter o conteúdo da página
    # Verifica se a requisição foi bem-sucedida (código de status 200)
    if response.status_code == 200:
        # Utiliza BeautifulSoup para analisar o HTML da página
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extrai o texto do corpo da página
        if URL.__contains__('g1.globo.com') or URL.__contains__('oglobo.globo.com',):
            texto = '<br>'.join([paragrafo.get_text() for paragrafo in soup.find_all('p', class_='content-text__container')])
            texto = texto.replace('\r', '<br>')
            texto = texto.replace('\n', '<br>')
            texto = texto.replace('\t', ' ')
            print('############## G1')
        else:
            texto = '<br>'.join([paragrafo.get_text() for paragrafo in soup.find_all('p')])
            texto = texto.replace('\r', '<br>')
            texto = texto.replace('\n', '<br>')
            texto = texto.replace('\t', ' ')
            print('############## OUTROS')
        return texto
    else:
        print(f"Erro ao acessar a página. Código de status: {response.status_code} - {response.text}")
        return None


def get_final_redirect_url_curl(initial_url, max_retries=3):
    attempts = 0
    while attempts < max_retries:
        try:
            # Usar o comando curl para seguir redirecionamentos e obter a URL final
            curl_command = ['curl', '-m 30', '-s', '--location', '-o', '/dev/null', '-w', '%{url_effective}', initial_url]
            final_url = subprocess.check_output(curl_command, universal_newlines=True).strip()

            # Decodificar a URL final que está codificada
            final_url = unquote(final_url)
            final_text = extrair_texto_pagina(final_url)

            out = {
                'final_url': final_url,
                'text': final_text
            }

            return out
        except Exception as e:
            attempts += 1
            time.sleep(random.uniform(1, 3))
            print(f"Tentativa {attempts} - Erro ao obter a página: {e}")

    print(f"Falha após {max_retries} tentativas. Não foi possível obter a URL final.")
    return None


def parse_rss_feed(feed, max_workers=20):
    resultados = []

    print(f'antes {len(feed.entries)}')

    # para cada link do google, busca destino final do link
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_url = {executor.submit(get_final_redirect_url_curl, entry.link, 2): entry for entry in feed.entries}
        seq = 0
        for future in concurrent.futures.as_completed(future_to_url):
            seq += 1
            # print(seq)
            entry = future_to_url[future]
            try:
                final_url = future.result()
                if final_url:
                    resultado = {
                        "title": BeautifulSoup(entry.summary, 'html.parser').a.get_text(),
                        "id_original": entry.id,
                        "url": final_url['final_url'],
                        "text": final_url['text'],
                        "source_title": getattr(entry, 'source', {}).get('title', 'Unknown source'),
                        "published": entry.published,
                        }
                    # print(f'---------- {entry}')
                    resultados.append(resultado)
                    # print(resultado)
            except Exception as exc:
                print(f'Erro ao processar URL {entry.link}: {exc}')

    return resultados


def gerer_link(dias, LANG, COUNTRY, tags_chave_and, tags_chave_or):
    HTTP_AGENT = 'Mozilla/5.0 (X11; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/123.0'
    CEID = 'BR&3Dpt-419'
    BASE_URL = 'https://news.google.com/rss/search'

    # Acrescenta delimitador para unir as palavras da TAGs
    str_chave_and = ' AND '.join(delimitar_palavras(tags_chave_and))
    str_chave_or = ' OR '.join(delimitar_palavras(tags_chave_or))

    # Constroi str da query conforme tags "AND" e "OR" preenchidas
    if str_chave_and and str_chave_or:
        query = f'({str_chave_and}) AND ({str_chave_or})'
    elif str_chave_and:
        query = f'({str_chave_and})'
    else:
        query = f'({str_chave_or})'

    query_pattern = f'{BASE_URL}?q={query}%20when%3A{dias}d&hl={LANG}&gl={COUNTRY}&ceid={CEID}'

    print('query:::',query_pattern)
    return query_pattern


def delimitar_palavras(palavras):
    out = []
    for w in palavras:
        if ' ' in w:
            out.append(f'"{w}"')
        else:
            out.append(f'{w}')
    return out
