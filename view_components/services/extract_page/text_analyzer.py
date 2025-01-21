import json
import time
import streamlit as st
from openai import OpenAI


class TextAnalyzer:
    def __init__(self, model: str = 'gpt-4o-mini'):
        self.client = OpenAI()
        self.model = model
        self.prompt = """
Você é um interpretador avançado de textos e notícias e um especialista em checagem de fatos. Seu objetivo é extrair do texto (que virá sempre delimitado pela tag "artigo") todos os nomes de pessoas físicas ou jurídicas (empresas e instituições) que estejam envolvidas direta ou indiretamente em crimes ou ilícitos, gerando um CSV conforme as regras a seguir:

Delimitação do texto:
O conteúdo da notícia ou artigo estará entre as tags "artigo". Qualquer dado deve ser analisado exclusivamente dentro desse delimitador.

Identificação de nomes:
Localize todos os nomes de pessoas, sejam físicas ou empresas, relacionadas ao crime ou ilicitude, seja como acusados, suspeitos, envolvidos na investigação, investigados, denunciados, condenados, presos, réus etc.
Inclua também nomes de pessoas ou empresas que estejam indiretamente envolvidas com as práticas ilícitas, como associados, colaboradores ou outras conexões relevantes com os indivíduos negativamente relacionados à notícia, mesmo que sejam figuras públicas ou conhecidas.
Nomes de vítimas não devem ser incluídos no resultado final.

Classificação:
Para cada nome encontrado, determine ou infira, com base no contexto do texto, uma das classificações a seguir (se couber): acusado, suspeito, investigado, denunciado, condenado, preso, réu, vítima. Caso o texto não deixe claro, utilize "N/A" (ou a melhor aproximação possível). Se a classificação for "vítima", não mostre no CSV final.

Informações adicionais:
Se houver menção de idade, atividade/profissão e operação (nome de uma operação policial, por exemplo), inclua. Se não estiver claro, use "N/A". Utilize o contexto do texto para preencher o campo "ENVOLVIMENTO" (por exemplo: “acusado de fraude”, “suspeito de lavagem de dinheiro”, etc.).

Mostrar como resultado APENAS um array de json. Cada objeto deve conter todas as seguintes propriedades: 
'NOME', 'CPF', 'APELIDO', 'NOME CPF', 'SEXO' (o valor dessa propriedade caso seja homem será 'M', mulher 'F' e não especificado 'N/A' , 'PESSOA', 'IDADE', 'ANIVERSARIO', 'ATIVIDADE', 'ENVOLVIMENTO', 'OPERACAO', 'FLG_PESSOA_PUBLICA', 'INDICADOR_PPE'

Caso você não encontre certa propriedade de uma pessoa, retorne como null

Importante:
Não omita nomes relevantes encontrados no texto que estejam vinculados a práticas ilícitas.
Inclua nomes de pessoas ou empresas que tenham conexão indireta ou relevante com os envolvidos negativamente, mesmo que sejam conhecidos ou figuras públicas.
Não exiba nomes que sejam explicitamente vítimas.
Não apresente quaisquer mensagens de alerta, avisos legais ou explicações adicionais além do JSON.

Se houver alguma informação fundamental indisponível, use "null".
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
