import json
import re
import time
import streamlit as st
from openai import OpenAI


class TextAnalyzer:
    def __init__(self, model: str = 'gpt-4o'):
        self.client = OpenAI()
        self.model = model
        self.prompt = """
            Você atuará como um interpretador avançado de textos jornalísticos e checador de fatos, com foco em identificar nomes de pessoas ou entidades envolvidas em crimes ou outros atos ilicitos.
            Seu objetivo é  localizar e extrair os nomes e as informações solicitadas, apresentando somente o resultado em formato de array JSON, onde cada nome será um elemento.
            O texto a ser analisado será fornecido entre as tags artigo.
            Para cada NOME, ENTIDADE ou EMPRESA encontrada no texto, resuma seu envolvimento em possíveis crimes.
            Em seguida, classifique cada um conforme o contexto de envolvimento no texto, utilizando um dos seguintes termos: acusado, suspeito, investigado, denunciado, condenado, preso ou réu.
            Inclua *APENAS* nomes próprios de pessoas, empresas ou entidades, evitando gerneralizações como função, profissao, etc.
            Não incluir nos resultados pessoas que não estejam diretamente envolvidas ou suspeitas de crime.
            Não inclua nomes de vítimas ou pessoas mencionadas como vítimas.
            A resposta não deve conter nenhum outro texto ou formatação além de um array de objetos JSON.
            
            Cada elemento do array deve conter as seguintes propriedades, mesmo que o valor seja null:
            
                NOME (nome da pessoa ou entidade encontrada na notícia)
                CPF (CPF para pessoa fisica ou CNPJ para pessoal jurídica encontrada na notícia)
                APELIDO
                NOME_CPF (fixo null)
                SEXO (usar 'M' para homens, 'F' para mulheres)
                PESSOA ('F' para pessoal física 'J' para pessoa jurídica ou entidades)
                IDADE (idade da pessoa, se encontada no texto)
                ANIVERSARIO (data de nascimento da pessoa, se encontada no texto )
                ATIVIDADE (ocupação, cargo ou atividade principal da pessoa)
                ENVOLVIMENTO (termo de classificação: acusado, suspeito, investigado, denunciado, condenado, preso, réu)
                OPERACAO (nome da operação policial ou judicial)
                FLG_PESSOA_PUBLICA (fixo false)
                INDICADOR_PPE (fixo false)
                ENVOLVIMENTO_GOV (retornar true se houver envolvimento com governo, ou false)
            
            Importante: Se não houver nenhum nome, retorne um array JSON vazio ( Exemplo: [] )
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

            resposta = response.choices[0].message.content.strip()

            print(f"Resposta recebida: {resposta}")

            match = re.search(r'```json\s*(\[\s*{.*}\s*\])\s*```', resposta, re.DOTALL)
            if match:
                json_str = match.group(1)
            else:
                json_str = resposta

            if json_str:
                try:
                    resposta_dict = json.loads(json_str)
                except json.JSONDecodeError as json_err:
                    print(f"Erro ao decodificar JSON: {json_err}")
                    return []
            else:
                print("Resposta vazia ou formato inesperado.")
                return []

            if isinstance(resposta_dict, list):
                for rd in resposta_dict:
                    if rd.get('NOME'):
                        no_none_name.append(rd)
            else:
                print("A resposta JSON não é uma lista conforme esperado.")
                return []

            return no_none_name

        except Exception as e:
            print(f"Exceção geral: {e}")
            return []