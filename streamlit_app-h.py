import streamlit as st
import random
import csv
import io
import pandas as pd
from datetime import datetime, timedelta

# ---------------------------------------------
# Configuração inicial
# ---------------------------------------------
st.set_page_config(page_title="Gerador de documentos fictícios (Fluxo)", layout="wide")
st.title("Gerador de documentos fictícios (Fluxo) (v2.0.0)")

# ---------------------------------------------
# Botão lateral para reset
# ---------------------------------------------
if st.sidebar.button("🔁 Resetar todos os dados"):
    st.session_state.clear()
    st.experimental_rerun()

# ---------------------------------------------
# Inicialização do session_state
# ---------------------------------------------
def init_state(key, default):
    if key not in st.session_state:
        st.session_state[key] = default

# Inicializa estados
init_state("data_inicio", datetime(2025, 1, 1))
init_state("data_fim", datetime(2025, 12, 31))
init_state("lista_unidades", [])
init_state("entradas_codigos", [])
init_state("saidas_codigos", [])
init_state("lista_tesouraria", [])
init_state("lista_cc", [])
init_state("lista_tipos", [])

# ---------------------------------------------
# Menu lateral
# ---------------------------------------------
menu_itens = [
    "Observações da função",
    "Período",
    "Unidades",
    "Classificações",
    "Tesouraria",
    "Centro de Custo (Opcional)",
    "Tipos de Documento (Opcional)",
    "Gerar CSV"
]

# Determina aba ativa a partir do query param
query_params = st.query_params
aba_query = query_params.get("aba", [menu_itens[0]])[0]
if aba_query not in menu_itens:
    aba_query = menu_itens[0]
st.session_state.setdefault("aba_ativa", aba_query)
opcao = st.session_state["aba_ativa"]

# ---------------------------------------------
# Menu lateral com CSS
# ---------------------------------------------
st.sidebar.markdown("""
    <style>
    .menu-botao {
        padding: 10px 15px;
        border-radius: 8px;
        margin-bottom: 6px;
        font-weight: 500;
        color: #444;
        background-color: #f5f5f5;
        border: 1px solid #ddd;
        transition: all 0.2s ease-in-out;
        cursor: pointer;
        text-align: left;
        display: block;
        width: 100%;
        box-sizing: border-box;
        text-decoration: none;
    }
    .menu-botao:hover {
        background-color: #ffe082;
    }
    .menu-ativo {
        background-color: #FFD700 !important;
        color: black !important;
        font-weight: 700 !important;
        border: 1px solid #d4af37;
    }
    </style>
""", unsafe_allow_html=True)

for item in menu_itens:
    href = f"?aba={item.replace(' ', '%20')}"
    if item == opcao:
        st.sidebar.markdown(f"<a class='menu-botao menu-ativo' href='{href}'>{item}</a>", unsafe_allow_html=True)
    else:
        st.sidebar.markdown(f"<a class='menu-botao' href='{href}'>{item}</a>", unsafe_allow_html=True)

# ---------------------------------------------
# Função para gerar templates XLSX
# ---------------------------------------------
def gerar_template_xlsx(tipo):
    output = io.BytesIO()
    if tipo == "entrada":
        df = pd.DataFrame({"codigo": ["E001", "E002"], "nome": ["Exemplo de entrada", "Venda de produto"]})
        sheet_name = "classificacoes_entrada"
    elif tipo == "saida":
        df = pd.DataFrame({"codigo": ["S001", "S002"], "nome": ["Exemplo de saída", "Pagamento de fornecedor"]})
        sheet_name = "classificacoes_saida"
    elif tipo == "unidades":
        df = pd.DataFrame({"codigo": ["01", "02", "03"], "nome": ["Matriz", "Filial SP", "Filial RJ"]})
        sheet_name = "unidades"
    elif tipo == "tesouraria":
        df = pd.DataFrame({"codigo": ["T001", "T002"], "nome": ["Conta Banco 1", "Caixa Interno"]})
        sheet_name = "tesouraria"
    elif tipo == "centro_custo":
        df = pd.DataFrame({"codigo": ["CC01", "CC02"], "nome": ["Administrativo", "Operacional"]})
        sheet_name = "centro_custo"
    elif tipo == "tipos_doc":
        df = pd.DataFrame({"codigo": ["NF", "REC"], "nome": ["Nota Fiscal", "Recibo"]})
        sheet_name = "tipos_documento"
    else:
        df = pd.DataFrame()
        sheet_name = "Sheet1"
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    output.seek(0)
    return output.getvalue()

# ---------------------------------------------
# Funções auxiliares
# ---------------------------------------------
def random_date(start, end):
    delta = end - start
    return start + timedelta(days=random.randint(0, delta.days))

def random_payment_date(due_date):
    if random.random() < 0.5:
        shift = random.randint(-5, 5)
        return due_date + timedelta(days=shift)
    else:
        return ""

def random_valor():
    return round(random.uniform(1, 101000), 2)

# ---------------------------------------------
# Abas
# ---------------------------------------------
if opcao == "Observações da função":
    st.markdown("""
    <div style="text-align: justify; font-size:18px; border:1px solid #ddd; border-radius:10px; padding:15px; background-color:#f9f9f9;">
        <h3 style="text-align:center; color:#333;">Observações sobre a função</h3>
        <ul>
            <li>Gera documentos fictícios de entradas e saídas financeiras.</li>
            <li>Campo de unidade preenchido com códigos cadastrados.</li>
            <li>Classificações podem ser preenchidas via template ou manualmente.</li>
            <li>Período definido pelas datas inicial e final.</li>
            <li>Datas de vencimento e liquidação simuladas aleatoriamente.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

elif opcao == "Período":
    st.header("Selecionar período dos registros")
    col1, col2 = st.columns(2)
    with col1:
        data_inicio_str = st.text_input("Data inicial (dd/mm/aaaa)", value=st.session_state.data_inicio.strftime("%d/%m/%Y"))
        try:
            st.session_state.data_inicio = datetime.strptime(data_inicio_str, "%d/%m/%Y")
        except:
            st.error("Formato de data inicial inválido!")
    with col2:
        data_fim_str = st.text_input("Data final (dd/mm/aaaa)", value=st.session_state.data_fim.strftime("%d/%m/%Y"))
        try:
            st.session_state.data_fim = datetime.strptime(data_fim_str, "%d/%m/%Y")
        except:
            st.error("Formato de data final inválido!")

elif opcao == "Unidades":
    st.header("Identificação de Unidades")
    col1, col2 = st.columns(2)
    with col1:
        st.download_button("Baixar modelo (XLSX)", gerar_template_xlsx("unidades"), file_name="unidades_template.xlsx")
    with col2:
        arquivo = st.file_uploader("Importar arquivo de Unidades", type=["xlsx"])
    if arquivo:
        df = pd.read_excel(arquivo)
        if "codigo" in df.columns:
            st.session_state.lista_unidades = df["codigo"].dropna().astype(str).tolist()
            st.success(f"{len(st.session_state.lista_unidades)} unidades importadas.")
            st.dataframe(df)
        else:
            st.error("Coluna 'codigo' não encontrada.")
    else:
        val = st.text_area("Lista de unidades (separadas por vírgula)", value="01,02,03")
        st.session_state.lista_unidades = [v.strip() for v in val.split(",") if v.strip()]

elif opcao == "Classificações":
    st.header("Importar Classificações")
    col1, col2 = st.columns([48, 48])
    with col1:
        st.subheader("Entradas")
        st.download_button("Modelo Entrada", gerar_template_xlsx("entrada"), file_name="entrada.xlsx")
        arq_e = st.file_uploader("Importar Entradas", type=["xlsx"])
        if arq_e:
            df = pd.read_excel(arq_e)
            if {"codigo", "nome"}.issubset(df.columns):
                st.session_state.entradas_codigos = df["codigo"].dropna().astype(str).tolist()
                st.dataframe(df)
            else:
                st.error("Colunas 'codigo' e 'nome' obrigatórias.")
        else:
            val = st.text_area("Entradas (separadas por vírgula)", value="E001,E002")
            st.session_state.entradas_codigos = [v.strip() for v in val.split(",") if v.strip()]
    with col2:
        st.subheader("Saídas")
        st.download_button("Modelo Saída", gerar_template_xlsx("saida"), file_name="saida.xlsx")
        arq_s = st.file_uploader("Importar Saídas", type=["xlsx"])
        if arq_s:
            df = pd.read_excel(arq_s)
            if {"codigo", "nome"}.issubset(df.columns):
                st.session_state.saidas_codigos = df["codigo"].dropna().astype(str).tolist()
                st.dataframe(df)
            else:
                st.error("Colunas 'codigo' e 'nome' obrigatórias.")
        else:
            val = st.text_area("Saídas (separadas por vírgula)", value="S001,S002")
            st.session_state.saidas_codigos = [v.strip() for v in val.split(",") if v.strip()]

elif opcao == "Tesouraria":
    st.header("Identificação da Tesouraria")
    col1, col2 = st.columns(2)
    with col1:
        st.download_button("Modelo Tesouraria", gerar_template_xlsx("tesouraria"), file_name="tesouraria.xlsx")
    with col2:
        arq = st.file_uploader("Importar Tesouraria", type=["xlsx"])
    if arq:
        df = pd.read_excel(arq)
        if "codigo" in df.columns:
            st.session_state.lista_tesouraria = df["codigo"].dropna().astype(str).tolist()
            st.dataframe(df)
        else:
            st.error("Coluna 'codigo' obrigatória.")
    else:
        val = st.text_area("Contas Tesouraria (separadas por vírgula)", value="T001,T002")
        st.session_state.lista_tesouraria = [v.strip() for v in val.split(",") if v.strip()]

elif opcao == "Centro de Custo (Opcional)":
    st.header("Centro de Custo")
    col1, col2 = st.columns(2)
    with col1:
        st.download_button("Modelo Centro de Custo", gerar_template_xlsx("centro_custo"), file_name="cc.xlsx")
    with col2:
        arq = st.file_uploader("Importar Centro de Custo", type=["xlsx"])
    if arq:
        df = pd.read_excel(arq)
        if "codigo" in df.columns:
            st.session_state.lista_cc = df["codigo"].dropna().astype(str).tolist()
            st.dataframe(df)
        else:
            st.error("Coluna 'codigo' obrigatória.")
    else:
        val = st.text_area("Centros de Custo (separadas por vírgula)", value="CC01,CC02")
        st.session_state.lista_cc = [v.strip() for v in val.split(",") if v.strip()]

elif opcao == "Tipos de Documento (Opcional)":
    st.header("Tipos de Documento")
    col1, col2 = st.columns(2)
    with col1:
        st.download_button("Modelo Tipos", gerar_template_xlsx("tipos_doc"), file_name="tipos.xlsx")
    with col2:
        arq = st.file_uploader("Importar Tipos de Documento", type=["xlsx"])
    if arq:
        df = pd.read_excel(arq)
        if "codigo" in df.columns:
            st.session_state.lista_tipos = df["codigo"].dropna().astype(str).tolist()
            st.dataframe(df)
        else:
            st.error("Coluna 'codigo' obrigatória.")
    else:
        val = st.text_area("Tipos de Documento (separadas por vírgula)", value="NF,REC")
        st.session_state.lista_tipos = [v.strip() for v in val.split(",") if v.strip()]

elif opcao == "Gerar CSV":
    st.header("Gerar Arquivo CSV")
    num_registros = st.number_input("Número de registros", min_value=10, max_value=1000, value=100)
    if st.button("Gerar CSV"):
        registros = []
        for i in range(1, num_registros + 1):
            tipo = random.choice(["E", "S"])
            descricao = random.choice(st.session_state.entradas_codigos if tipo=="E" else st.session_state.saidas_codigos)
            valor = random_valor()
            venc = random_date(st.session_state.data_inicio, st.session_state.data_fim)
            pag = random_payment_date(venc)
            registros.append([
                i, tipo, valor, random.choice(st.session_state.lista_unidades or ["01","02","03"]),
                venc.strftime("%d/%m/%Y"), pag.strftime("%d/%m/%Y") if pag else "",
                descricao,
                f"C{random.randint(1,50)}" if tipo=="E" else f"F{random.randint(1,50)}",
                random.choice(st.session_state.lista_tesouraria or ["T001","T002"]),
                random.choice(st.session_state.lista_cc or [""]),
                random.choice(st.session_state.lista_tipos or [""])
            ])
        df = pd.DataFrame(registros, columns=["documento","tipo","valor","cod_unidade","data_venc","data_liq",
                                              "descricao","cliente_fornecedor","tesouraria","centro_custo","tipo_documento"])
        st.download_button("Download CSV", df.to_csv(index=False).encode("utf-8-sig"), file_name="documentos.csv")
        st.success(f"{len(registros)} registros gerados!")