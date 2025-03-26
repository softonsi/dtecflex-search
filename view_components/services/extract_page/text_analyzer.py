import json
import re
from openai import OpenAI


class TextAnalyzer:
    def __init__(self, model: str = 'gpt-4o', notice_categoria: str = 'normal'):
        self.client = OpenAI()
        self.notice_categoria = notice_categoria
        self.model = model
        
        if self.notice_categoria == 'Ambiental':
            self.prompt = self.prompt_is_ambiental
        else:
            self.prompt = self.prompt_not_ambiental
    
    prompt_not_ambiental = """
        Você atuará como um interpretador avançado de textos jornalísticos e checador de fatos, com foco em identificar nomes de pessoas ou entidades envolvidas em crimes ou outros atos ilicitos.
        Seu objetivo é  localizar e extrair os nomes e as informações solicitadas, apresentando somente o resultado em formato de array JSON, onde cada nome será um elemento.
        O texto a ser analisado será fornecido entre as tags artigo.
        Para cada NOME, ENTIDADE ou EMPRESA encontrada no texto, resuma seu envolvimento em possíveis crimes.
        Em seguida, classifique cada um conforme o contexto de envolvimento no texto, utilizando um dos seguintes termos: acusado, suspeito, investigado, denunciado, condenado, preso ou réu.
        Inclua *APENAS* nomes próprios de pessoas, empresas ou entidades, evitando generalizações como função, profissão, etc.
        Não incluir nos resultados pessoas que não estejam diretamente envolvidas ou suspeitas de crime.
        Não inclua nomes de vítimas ou pessoas mencionadas como vítimas.
        A resposta não deve conter nenhum outro texto ou formatação além de um array de objetos JSON.
        
        Cada elemento do array deve conter as seguintes propriedades, mesmo que o valor seja null:
        
            NOME (nome da pessoa ou entidade encontrada na notícia)
            CPF (CPF para pessoa física ou CNPJ para pessoa jurídica encontrada na notícia)
            APELIDO
            NOME_CPF (fixo null)
            SEXO (usar 'M' para homens, 'F' para mulheres)
            PESSOA ('F' para pessoa física 'J' para pessoa jurídica ou entidades)
            IDADE (idade da pessoa, se encontrada no texto)
            ANIVERSARIO (data de nascimento da pessoa, se encontrada no texto )
            ATIVIDADE (ocupação, cargo ou atividade principal da pessoa)
            ENVOLVIMENTO (termo de classificação: acusado, suspeito, investigado, denunciado, condenado, preso, réu)
            OPERACAO (nome da operação policial ou judicial)
            FLG_PESSOA_PUBLICA (fixo false)
            INDICADOR_PPE (fixo false)
            ENVOLVIMENTO_GOV (retornar true se houver envolvimento com governo, ou false)
        
        Importante: Se não houver nenhum nome, retorne um array JSON vazio ( Exemplo: [] )
    """
    
    prompt_is_ambiental = """
        Você atuará como um interpretador avançado de textos jornalísticos e checador de fatos, com foco em identificar nomes de pessoas ou entidades envolvidas em atividades ambientais, incluindo crimes, infrações ou outros tipos de envolvimento com questões ambientais.
        Seu objetivo é localizar e extrair os nomes e as informações solicitadas, apresentando somente o resultado em formato de array JSON, onde cada nome será um elemento.
        O texto a ser analisado será fornecido entre as tags artigo.
        Para cada NOME, ENTIDADE ou EMPRESA encontrada no texto, resuma seu envolvimento em possíveis crimes, infrações ambientais, projetos, denúncias ou outras questões relacionadas a atividades ambientais.
        Em seguida, classifique cada um conforme o contexto de envolvimento no texto, utilizando um dos seguintes termos: acusado, suspeito, investigado, denunciado, condenado, preso, réu, envolvido, colaborador, responsável, líder, organizador, participante ou outros termos relacionados à categoria ambiental.
        Inclua *APENAS* nomes próprios de pessoas, empresas ou entidades, evitando generalizações como função, profissão, etc.
        Não incluir nos resultados pessoas que não estejam diretamente envolvidas ou suspeitas de crimes ou infrações ambientais.
        Não inclua nomes de vítimas ou pessoas mencionadas como vítimas.
        A resposta não deve conter nenhum outro texto ou formatação além de um array de objetos JSON.
                    
        Cada elemento do array deve conter as seguintes propriedades, mesmo que o valor seja null:
                    
            NOME (nome da pessoa ou entidade encontrada na notícia)
            CPF (CPF para pessoa física ou CNPJ para pessoa jurídica encontrada na notícia)
            APELIDO
            NOME_CPF (fixo null)
            SEXO (usar 'M' para homens, 'F' para mulheres)
            PESSOA ('F' para pessoa física, 'J' para pessoa jurídica ou entidades)
            IDADE (idade da pessoa, se encontrada no texto)
            ANIVERSARIO (data de nascimento da pessoa, se encontrada no texto)
            ATIVIDADE (ocupação, cargo ou atividade principal da pessoa)
            ENVOLVIMENTO (termo de classificação: acusado, suspeito, investigado, denunciado, condenado, preso, réu, envolvido, colaborador, responsável, líder, organizador, participante, etc.)
            OPERACAO (nome da operação policial ou judicial, se houver)
            FLG_PESSOA_PUBLICA (fixo false)
            INDICADOR_PPE (fixo false)
            ENVOLVIMENTO_GOV (retornar true se houver envolvimento com o governo, ou false)
                    
        Importante: Se não houver nenhum nome, retorne um array JSON vazio (Exemplo: []).
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
    