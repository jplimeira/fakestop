
# 🛡️ FAKESTOP - Verificador de Notícias com IA

Este projeto foi desenvolvido por **Jayro Pereira Limeira**, como avaliação do **primeiro bimestre** da matéria de IA
do **quinto semestre** da faculdade, sob orientação do professor **Igor Oliveira Vasconcelos**.

## 📌 Sobre o projeto

O **FAKESTOP** é um sistema de verificação de notícias utilizando **IA com agentes inteligentes (CrewAI)**, que tem como objetivo identificar se uma notícia é **VERDADEIRA✅**, **FALSA🤥** ou **DUVIDOSA🫤** com base em evidências e análise linguística. O sistema realiza:

- Coleta de fontes confiáveis (como G1, BBC, Google Fact Check)
- Revisão linguística do texto (corrigindo clickbait, alarmismo, etc.)
- Verificação de fatos com base nas fontes
- Classificação final da notícia com justificativa
- Armazenamento de todas as análises em um banco de dados local
- Interface amigável com Streamlit

---

## 🛠️ Como executar o projeto

**obs: Está no repositório dois códigos do programa, mas um deles é para execução no terminal, o arquivo 'fakestop.py',**
**e o outro foi o que fiz por último, ultilizando o streamlit, o arquivo 'fakestop_app.py.**

### 1. 🔃 Clone o repositório

```bash
git clone https://github.com/jplimeira/fakestop.git
cd fakestop
```

### 2. 🐍 Crie e ative o ambiente virtual

#### Para **Windows (CMD)**:

```bash
python -m venv venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
venv\Scripts\activate
```

#### Para **PowerShell**:

```powershell
python -m venv venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

#### Para **Linux/MacOS**:

```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 3. 📦 Instale as dependências

```bash
pip install -r requiriments.txt
```

> Certifique-se de que o arquivo `requiriments.txt` contenha:
> ```
> streamlit
> crewai
> python-dotenv
> openai
> ```

---

### 4. 🔑 Configure sua chave da OpenAI

Crie um arquivo chamado `.env` no diretório raiz e insira sua chave da OpenAI:

```
OPENAI_API_KEY=sua_chave_aqui
```

---

### 5. 🚀 Execute o aplicativo

No arquivo 'fakestop.py': apenas um run without debugging.

No arquivo 'fakestop_app.py': 

```bash
streamlit run fakestop_app.py
```

---

## 🧠 Como funciona

A partir de um texto de notícia digitado pelo usuário:

1. **Agente Coletor** busca fontes confiáveis sobre o tema.
2. **Agente Linguístico** revisa o texto, corrigindo exageros e clickbait.
3. **Agente Verificador** checa a veracidade com base nas fontes.
4. **Agente Classificador** define se a notícia é verdadeira, falsa ou duvidosa.
5. Todos os resultados são salvos em um banco **SQLite**.
6. A aba **📚 Ver histórico** permite visualizar análises passadas.

---

## 📚 Tecnologias utilizadas

- 🧠 [CrewAI](https://pypi.org/project/crewai/)
- 🧠 [OpenAI API](https://platform.openai.com/)
- 🎨 [Streamlit](https://streamlit.io/)
- 🗂️ SQLite
- 🐍 Python 3.11+

---

## 📬 Contato

jayropl777@gmail.com
(82)98103-5207
Projeto desenvolvido por **Jayro Pereira Limeira**  
Aluno do 5º semestre | Professor: **Igor Oliveira Vasconcelos**

---
#
