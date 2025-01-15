import json
import time
import streamlit as st
from openai import OpenAI


class TextAnalyzer:
    def __init__(self, model: str = 'gpt-4o-mini'):
        self.client = OpenAI()
        self.model = model
        self.prompt = """
            Você irá atuar como interpretador avançado de textos, notícias e checagem de fatos. O objetivo principal é localizar nomes de pessoas envolvidas em crimes ou outras ilicitudes. Cada nome deverá ser listado com outras informações que podem ser obtidas na notícia e conforme as regras abaixo.
            O texto será fornecido delimitado com a tag "artigo"
            Localize cada NOME, ENTIDADE ou EMPRESA citada no texto, resumindo seu ENVOLVIMENTO em ilícitos ou crime e conforme contexto, crie uma CLASSIFICACAO como acusado, suspeito, investigado, denunciado, condenado, preso, réu, vítima.
            Não incluir nomes de vítimas.
            Não mostrar marcadores de markdown.
            Mostrar como resultado APENAS um array de json. Cada objeto deve conter todas as seguintes propriedades:
                'NOME', 'CPF', 'APELIDO', 'NOME CPF', 'SEXO' (o valor dessa propriedade caso seja homem será 'M', mulher 'F' e não especificado 'N/A'
                , 'PESSOA', 'IDADE', 'ANIVERSARIO', 'ATIVIDADE', 'ENVOLVIMENTO', 'OPERACAO', 'FLG_PESSOA_PUBLICA', 'INDICADOR_PPE'
            caso você não encontre certa propriedade de uma pessoa, retorne como null
        """

    def analyze_text(self, text: str) -> list:
        try:
            artigo = f"<artigo>\n{text}\n</artigo>"
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.prompt},
                    {"role": "user", "content": artigo}
                ]
            )
            no_none_name = []

            resposta = response.choices[0].message.content

            resposta_dict = json.loads(resposta)

            if isinstance(resposta_dict, list):
                timestamp = int(time.time())
                for i, item in enumerate(resposta_dict):
                    item['ID'] = f"extracted_{i}_{timestamp}"
                    item['deleted'] = False

            for rd in resposta_dict:
                if rd['NOME']:
                    no_none_name.append(rd)

            return no_none_name

        except Exception as e:
            st.error(f"Erro ao processar a chamada à API2222: {e}")
            return []
