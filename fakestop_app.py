# ---------------------- IMPORTAÇÕES E CONFIGURAÇÃO ----------------------
import os
import sqlite3
import streamlit as st
from crewai import Agent, Task, Process, Crew, LLM
from dotenv import load_dotenv
from datetime import datetime

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Instancia o modelo da OpenAI (gpt-4o-mini)
llm = LLM(model='gpt-4o-mini', api_key=OPENAI_API_KEY)

# ---------------------- BANCO DE DADOS ----------------------
# Conecta ou cria o banco de dados SQLite para armazenar análises
conn = sqlite3.connect("fakestop.db")
cursor = conn.cursor()
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

# ---------------------- INTERFACE STREAMLIT ----------------------
# Define configurações da página
st.set_page_config(page_title="FAKESTOP", layout="wide")
st.title("🛡️ FAKESTOP - Verificador de Notícias")

# Menu lateral com abas
aba = st.sidebar.radio("Escolha uma opção", ["🔍 Analisar nova notícia", "📚 Ver histórico"])

# ---------------------- ANÁLISE DE NOTÍCIA ----------------------
if aba == "🔍 Analisar nova notícia":
    noticia = st.text_area("Digite a notícia que deseja verificar", height=200)

    if st.button("Analisar notícia"):
        if not noticia.strip():
            st.error("Por favor, insira uma notícia para analisar.")
        else:
            with st.spinner("🔎 Executando análise..."):

                # ---------- AGENTE 1: Coletor de Fontes ----------
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

                tarefa_coletar = Task(
                    description=f"Pesquisa de fontes confiáveis para coletar informações {noticia}.",
                    expected_output="Relatório de fontes coletadas com data, links e resumos.",
                    agent=agente_coletor,
                    output_file="coleta_de_fontes.md"
                )

                # ---------- AGENTE 2: Linguístico ----------
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

                # ---------- AGENTE 3: Verificador de Fatos ----------
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

                # ---------- EXECUÇÃO DOS AGENTES EM SEQUÊNCIA ----------
                crew = Crew(
                    agents=[agente_coletor, agente_linguistico, agente_verificador],
                    tasks=[tarefa_coletar, tarefa_linguistica, tarefa_verificacao],
                    process=Process.sequential,
                    llm=llm
                )
                crew.kickoff(inputs={"noticia": noticia})

                # ---------- CLASSIFICAÇÃO FINAL ----------
                with open("linguistica.md", "r", encoding="utf-8") as f1, open("verificacao.md", "r", encoding="utf-8") as f2:
                    texto_final = "# Texto Jornalístico Revisado\n\n" + f1.read() + "\n\n# Relatório de Verificação de Fatos\n\n" + f2.read()

                with open("entrada_para_classificacao.md", "w", encoding="utf-8") as f_out:
                    f_out.write(texto_final)

                # ---------- AGENTE 4: Classificador ----------

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

                crew_classificador = Crew(
                    agents=[agente_classificador],
                    tasks=[tarefa_classificacao],
                    process=Process.sequential,
                    llm=llm
                )
                crew_classificador.kickoff()

                # ---------- LEITURA E ARMAZENAMENTO NO BANCO ----------
                with open("coleta_de_fontes.md", "r", encoding="utf-8") as f: fontes = f.read()
                with open("linguistica.md", "r", encoding="utf-8") as f: linguistica = f.read()
                with open("verificacao.md", "r", encoding="utf-8") as f: verificacao = f.read()
                with open("classificacao_final.md", "r", encoding="utf-8") as f: classificacao = f.read()

                conn = sqlite3.connect("fakestop.db")
                cursor = conn.cursor()
                cursor.execute('''
                INSERT INTO analises (noticia, fontes, analise_linguistica, verificacao_fatos, classificacao_final, data_analise)
                VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    noticia, fontes, linguistica, verificacao, classificacao,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ))
                conn.commit()
                conn.close()

                st.success("✅ Análise concluída com sucesso!")

                # ---------- EXIBIÇÃO DOS RESULTADOS ----------
                st.subheader("📌 Classificação Final")
                st.markdown(classificacao)

                with st.expander("📂 Fontes Coletadas"):
                    st.markdown(fontes)

                with st.expander("📝 Análise Linguística"):
                    st.markdown(linguistica)

                with st.expander("🔎 Verificação de Fatos"):
                    st.markdown(verificacao)

# ---------------------- ABA DE HISTÓRICO ----------------------
elif aba == "📚 Ver histórico":
    conn = sqlite3.connect("fakestop.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, noticia, data_analise FROM analises ORDER BY id DESC")
    registros = cursor.fetchall()

    if not registros:
        st.info("Nenhuma análise realizada ainda.")
    else:
        for id_, noticia, data in registros:
            with st.expander(f"📰 {noticia[:80]}... ({data})"):
                cursor.execute("SELECT fontes, analise_linguistica, verificacao_fatos, classificacao_final FROM analises WHERE id=?", (id_,))
                fontes, linguistica, verificacao, classificacao = cursor.fetchone()

                st.subheader("📌 Classificação Final")
                st.markdown(classificacao)

                with st.markdown("📂 Fontes Coletadas"):
                    st.markdown(fontes)

                with st.markdown("📝 Análise Linguística"):
                    st.markdown(linguistica)

                with st.markdown("🔎 Verificação de Fatos"):
                    st.markdown(verificacao)

    conn.close()
