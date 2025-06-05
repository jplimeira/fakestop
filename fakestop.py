# ---------------------- IMPORTAÇÕES ----------------------
import os
import sqlite3
from crewai import Agent, Task, Process, Crew, LLM
from dotenv import load_dotenv
from datetime import datetime

# ---------------------- BANCO DE DADOS ----------------------
# Conecta ou cria o banco de dados SQLite
conn = sqlite3.connect("fakestop.db")
cursor = conn.cursor()

# Cria a tabela se não existir
cursor.execute('''
CREATE TABLE IF NOT EXISTS analises (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    noticia TEXT,
    fontes TEXT,
    analise_linguistica TEXT,
    verificacao_fatos TEXT,
    classificacao_final TEXT,
    data_analise TEXT
)
''')
conn.commit()
conn.close()

# ---------------------- CONFIGURAÇÃO DE AMBIENTE E MODELO ----------------------
# Carrega variáveis do .env
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Inicializa o modelo LLM
llm = LLM(model='gpt-4o-mini', api_key=OPENAI_API_KEY)

# ---------------------- ENTRADA DO USUÁRIO ----------------------
# Recebe a notícia do usuário
noticia = input("Informe a notícia que deseja verificar: ")
if not noticia.strip():
    raise ValueError("Você deve informar uma notícia para verificar.")

# ---------------------- AGENTE 1: COLETOR DE FONTES ----------------------
# Define o agente coletor de fontes confiáveis
agente_coletor = Agent(
    role='Jornalista investigativo',
    goal='''Você é um jornalista investigativo e precisa pesquisar fontes confiáveis para coletar 
    infomações sobre a temática {noticia} em sites como o https://g1.globo.com, https://bbc.com, 
    https://toolbox.google.com/factcheck/explorer/search/list:recent;hl=pt.''',
    verbose=True,
    memory=True,
    llm=llm,
    backstory='Você é um jornalista investigativo experiente sobre pesquisar notícias tipo {noticia}'
)

# Define a tarefa do agente coletor
tarefa_coletar = Task(
    description="Pesquisa de fontes confiáveis para coletar informações  {noticia}.",
    expected_output="Relatório de fontes coletadas com data, links e resumos.",
    agent=agente_coletor,
    output_file="coleta_de_fontes.md"
)

# ---------------------- AGENTE 2: LINGUÍSTICO ----------------------
# Define o agente responsável pela análise linguística
agente_linguistico = Agent(
    role='Agente linguístico',
    goal='''Aplique técnicas de processamento de linguagem para avaliar o estilo textual,
    verificando uso excessivo de adjetivos, linguagem alarmista e clickbait, identificar o
    idioma e fazer a tradução para o português Brasil, aplicar a avaliação textual no texto.''',
    verbose=True,
    memory=True,
    llm=llm,
    backstory='Você é um agente linguístico experiente, que avalia a qualidade textual'
)

# Define a tarefa do agente linguístico
tarefa_linguistica = Task(
    description="Analisar o texto e avaliar o estilo textual através dos parâmetros definidos no agente.",
    expected_output='''Relatório de texto revisado, com linguagem adequada, sem exageros e" \
    traduzido para o português Brasil, se for realmente necessário.''',
    agent=agente_linguistico,
    input="coleta_de_fontes.md",
    output_file="linguistica.md"
)

# ---------------------- AGENTE 3: VERIFICADOR DE FATOS ----------------------
# Define o agente verificador de fatos
agente_verificador = Agent(
    role='Verificador de fatos',
    goal='''Você é um verificador de fatos e precisa analisar as fontes coletadas pelo agente 
    coletor, verificando a veracidade das informações e a confiabilidade das fontes.''',
    verbose=True,
    memory=True,
    llm=llm,
    backstory='''Você é um especialista de fact-checking, que analisa a veracidade das informações coletadas
    e confirma a confiabilidade das fontes.'''
)

# Define a tarefa do verificador
tarefa_verificacao = Task(
    description="Analisar as fontes coletadas pelo agente coletor, verificando a veracidade das informações.",
    expected_output='''Relatório de verificação de fatos, com análise da veracidade das informações 
    e confiabilidade das fontes.''',
    agent=agente_verificador,
    input="linguistica.md",
    output_file="verificacao.md"
)

# ---------------------- EXECUÇÃO DA CREW PRINCIPAL ----------------------
# Define o processo com os três primeiros agentes
crew = Crew(
    agents=[agente_coletor, agente_linguistico, agente_verificador],
    tasks=[tarefa_coletar, tarefa_linguistica, tarefa_verificacao],
    process=Process.sequential,
    llm=llm
)

# Executa o processo principal
analise1 = crew.kickoff(inputs={'noticia': noticia})

# ---------------------- MONTAGEM DO TEXTO FINAL ----------------------
# Lê os relatórios e une para classificar
with open("linguistica.md", "r", encoding="utf-8") as f1, open("verificacao.md", "r", encoding="utf-8") as f2:
    texto_final = "# Texto Jornalístico Revisado\n\n" + f1.read() + "\n\n# Relatório de Verificação de Fatos\n\n" + f2.read()

# Escreve o arquivo de entrada para classificação
with open("entrada_para_classificacao.md", "w", encoding="utf-8") as f_out:
    f_out.write(texto_final)

# ---------------------- AGENTE 4: CLASSIFICADOR FINAL ----------------------
# Define o agente classificador
agente_classificador = Agent(
    role='Classificador de notícias',
    goal='''Você é um classificador de notícias e precisa analisar o artigo final, 
    classificando-o como verdadeiro, falso ou duvidoso.''',
    verbose=True,
    memory=True,
    llm=llm,
    backstory='''Você é um especialista em classificação de notícias, que analisa o artigo final 
    e classifica como verdadeiro, falso ou duvidoso.'''
)

# Define a tarefa de classificação
tarefa_classificacao = Task(
    description="Analisar o artigo final e classificá-lo como VERDADEIRO✅, FALSO🤥 ou DUVIDOSO🫤.",
    expected_output='''Classificação do artigo final como verdadeiro, falso ou duvidoso, 
    com justificativa da classificação.
    Dê uma resposta clara e objetiva,
    evitando jargões técnicos e explicando o raciocínio por trás da classificação.
    Leve em consideração as regras heurísticas simples que vou te passar agora: 
    se não encontra correspondência e texto alarmista = FALSO🤥
    se  encontra fonte confiável + texto neutro=VERDADEIRO✅
    e se encontrar apenas fontes não confiáveis ou não encontrar fontes = DUVIDOSO🫤,
    leve em conta que todas as fontes citadas no agente coletor são confiáveis.
    quando for dar a resposta, fale o resultado da classificação e justifique a sua resposta.''',
    agent=agente_classificador,
    input="entrada_para_classificacao.md",
    output_file="classificacao_final.md"
)

# Cria nova crew para a etapa de classificação
crew_classificador = Crew(
    agents=[agente_classificador],
    tasks=[tarefa_classificacao],
    process=Process.sequential,
    llm=llm
)

# Executa a classificação
crew_classificador.kickoff()

# ---------------------- EXIBE RESULTADOS NO TERMINAL ----------------------
print('------------------------------------')
print("\n----- VERIFICAÇÃO DOS FATOS -----\n")
print('------------------------------------')
with open("verificacao.md", "r", encoding="utf-8") as f:
    print(f.read())

print('---------------------------------------------')
print("\n----- CLASSIFICAÇÃO FINAL DA NOTÍCIA -----\n")
print('---------------------------------------------')
with open("classificacao_final.md", "r", encoding="utf-8") as f:
    resultado = f.read()

# ---------------------- ARMAZENAMENTO EM BANCO ----------------------
# Reabre conexão
conn = sqlite3.connect("fakestop.db")
cursor = conn.cursor()

# Lê todos os relatórios
with open("coleta_de_fontes.md", "r", encoding="utf-8") as f:
    fontes = f.read()

with open("linguistica.md", "r", encoding="utf-8") as f:
    linguistica = f.read()

with open("verificacao.md", "r", encoding="utf-8") as f:
    verificacao = f.read()

with open("classificacao_final.md", "r", encoding="utf-8") as f:
    classificacao = f.read()

# Insere dados no banco
cursor.execute('''
INSERT INTO analises (noticia, fontes, analise_linguistica, verificacao_fatos, classificacao_final, data_analise)
VALUES (?, ?, ?, ?, ?, ?)
''', (
    noticia,
    fontes,
    linguistica,
    verificacao,
    classificacao,
    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
))

conn.commit()
conn.close()

# Exibe classificação final no console
print(resultado)
