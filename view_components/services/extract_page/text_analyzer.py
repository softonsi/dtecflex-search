import json
import time
import streamlit as st
from openai import OpenAI


class TextAnalyzer:
    def __init__(self, model: str = 'gpt-4o-mini'):
        self.client = OpenAI()
        self.model = model
        self.prompt = """
            Você atuará como um interpretador avançado de textos jornalísticos e checador de fatos, com foco em identificar nomes de pessoas ou entidades envolvidas em crimes ou outras ilicitudes. Seu objetivo é extrair as informações solicitadas e apresentar somente o resultado em forma de array JSON.

            O texto a ser analisado será fornecido entre as tags artigo.

            Para cada ocorrência de NOME, ENTIDADE ou EMPRESA mencionada no texto, resuma seu envolvimento em possíveis ilicitudes ou crimes.

            Em seguida, classifique cada sujeito conforme o contexto de envolvimento no texto, utilizando um dos seguintes termos: acusado, suspeito, investigado, denunciado, condenado, preso ou réu.

            Não inclua nomes de vítimas ou pessoas apenas mencionadas como vítimas.
            A resposta não deve conter nenhum outro texto ou formatação além de um array de objetos JSON.

            Cada objeto no array deve conter todas as seguintes chaves (propriedades), mesmo que o valor seja null:

            NOME
            CPF
            APELIDO
            NOME CPF (caso haja uma forma específica de nome+CPF mencionada)
            SEXO (usar 'M' para homem, 'F' para mulher; caso não identificável, null)
            PESSOA (descrição curta, por exemplo "Político", "Empresário", "Cidadão comum", etc.)
            IDADE
            ANIVERSARIO
            ATIVIDADE (ocupação, cargo ou atividade principal se mencionado)
            ENVOLVIMENTO (termo de classificação: acusado, suspeito, investigado, denunciado, condenado, preso, réu)
            OPERACAO (nome da operação policial ou judicial, se houver)
            FLG_PESSOA_PUBLICA (retornar apenas true ou false)
            INDICADOR_PPE (retornar apenas true ou false para Pessoa Politicamente Exposta)
            ENVOLVIMENTO_GOV (retornar apenas true ou false se houver envolvimento com governo)
            Caso não haja informação suficiente para determinada chave (exceto as booleans), retorne o valor null.

            Para as propriedades booleanas (FLG_PESSOA_PUBLICA, INDICADOR_PPE, ENVOLVIMENTO_GOV), nunca retorne null; use true ou false.
            Importante: Se não houver menção de envolvidos, retorne um array JSON vazio: [].
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

            if isinstance(resposta, str) and resposta.strip():
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
            print(e)
            st.error(f"Erro ao processar a chamada à API2222: {e}")
            return []
