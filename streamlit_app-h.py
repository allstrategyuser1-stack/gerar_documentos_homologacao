import streamlit as st
import random
import csv
from datetime import datetime, timedelta
import pandas as pd
import io

# --- Configuração da página ---
st.set_page_config(page_title="Gerador de Documentos Fictícios (Fluxo)", layout="wide")

# --- CSS para as abas laterais ---
st.markdown("""
<style>
.sidebar-button {
    display: block;
    width: 100%;
    padding: 10px 14px;
    margin-bottom: 8px;
    border-radius: 8px;
    border: 1px solid #ddd;
    background-color: #f0f0f0;
    color: #333;
    font-weight: 500;
    text-align: center;
    cursor: pointer;
}
.sidebar-button:hover {
    background-color: #ffe082;
    color: black;
    border-color: #d4af37;
}
.sidebar-button.active {
    background-color: #FFD700;
    color: black;
    border: 1px solid #d4af37;
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)

# --- Abas do sistema ---
abas = [
    "Observações",
    "Período",
    "Unidades",
    "Classificações",
    "Tesouraria",
    "Centro de Custo (Opcional)",
    "Tipos de Documento (Opcional)",
    "Gerar CSV"
]

# --- Estado inicial ---
if "aba_ativa" not in st.session_state:
    st.session_state.aba_ativa = abas[0]

# --- Função para exibir menu lateral ---
def menu_lateral():
    st.sidebar.title("📑 Navegação")
    for aba in abas:
        classe = "sidebar-button active" if aba == st.session_state.aba_ativa else "sidebar-button"
        if st.sidebar.button(aba, key=aba):
            st.session_state.aba_ativa = aba
        st.sidebar.markdown(f"<div class='{classe}'>{aba}</div>", unsafe_allow_html=True)

menu_lateral()

# --- Função para gerar templates XLSX ---
def gerar_template_xlsx(tipo):
    output = io.BytesIO()
    if tipo == "entrada":
        df = pd.DataFrame({"codigo": ["E001", "E002"], "nome": ["Exemplo de entrada", "Venda de produto"]})
    elif tipo == "saida":
        df = pd.DataFrame({"codigo": ["S001", "S002"], "nome": ["Exemplo de saída", "Pagamento de fornecedor"]})
    elif tipo == "tesouraria":
        df = pd.DataFrame({"codigo": ["T001", "T002"], "nome": ["Tesouraria 1", "Tesouraria 2"]})
    elif tipo == "centro_custo":
        df = pd.DataFrame({"codigo": ["C001", "C002"], "nome": ["Centro 1", "Centro 2"]})
    elif tipo == "tipo_doc":
        df = pd.DataFrame({"codigo": ["TD001", "TD002"], "nome": ["NF", "Boleto"]})
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=tipo)
    output.seek(0)
    return output.getvalue()

# ======================================================
# CONTEÚDO DAS ABAS
# ======================================================

st.title(f" {st.session_state.aba_ativa}")

# --- Observações ---
if st.session_state.aba_ativa == "Observações":
    st.markdown("""
    <div style='text-align: justify; font-size:18px; border:1px solid #ddd;
    border-radius:10px; padding:15px; background-color:#f9f9f9;'>
    <h3 style='text-align:center;'>Observações sobre a Função</h3>
    <ul>
        <li>Gera documentos fictícios de entradas e saídas financeiras com base nos parâmetros definidos.</li>
        <li>As unidades e classificações podem ser importadas ou digitadas manualmente.</li>
        <li>Os períodos definem as datas de <b>vencimento</b>; a liquidação é aleatória.</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

# --- Aba Período ---
elif st.session_state.aba_ativa == "Período":
    st.header("Selecionar Período dos Registros")
    col1, col2 = st.columns(2)
    with col1:
        data_inicio_str = st.text_input("Data inicial (dd/mm/aaaa)", value="01/01/2025")
        try:
            st.session_state.data_inicio = datetime.strptime(data_inicio_str, "%d/%m/%Y")
        except:
            st.error("Formato inválido! Use dd/mm/aaaa")
    with col2:
        data_fim_str = st.text_input("Data final (dd/mm/aaaa)", value="31/12/2025")
        try:
            st.session_state.data_fim = datetime.strptime(data_fim_str, "%d/%m/%Y")
        except:
            st.error("Formato inválido! Use dd/mm/aaaa")

# --- Aba Unidades ---
elif st.session_state.aba_ativa == "Unidades":
    st.header("Identificação de Unidades")
    unidades_input = st.text_area("Lista de unidades (separadas por vírgula)", value="01,02,03")
    st.session_state.lista_unidades = [u.strip() for u in unidades_input.split(",") if u.strip()]

# --- Aba Classificações ---
elif st.session_state.aba_ativa == "Classificações":
    st.header("Importar Classificações")
    col_esq, col_dir = st.columns(2)

    with col_esq:
        st.subheader("Entradas")
        st.download_button("Baixar modelo", gerar_template_xlsx("entrada"),
                           "classificacoes_entrada.xlsx")
        arquivo_entradas = st.file_uploader("Importar lista de entradas", type=["xlsx"])
        if arquivo_entradas:
            df = pd.read_excel(arquivo_entradas)
            st.session_state.entradas = df["codigo"].tolist()
        else:
            entradas_input = st.text_area("Entradas (códigos separados por vírgula)", "E001,E002")
            st.session_state.entradas = [x.strip() for x in entradas_input.split(",")]

    with col_dir:
        st.subheader("Saídas")
        st.download_button("Baixar modelo", gerar_template_xlsx("saida"),
                           "classificacoes_saida.xlsx")
        arquivo_saidas = st.file_uploader("Importar lista de saídas", type=["xlsx"])
        if arquivo_saidas:
            df = pd.read_excel(arquivo_saidas)
            st.session_state.saidas = df["codigo"].tolist()
        else:
            saidas_input = st.text_area("Saídas (códigos separados por vírgula)", "S001,S002")
            st.session_state.saidas = [x.strip() for x in saidas_input.split(",")]

# --- Aba Tesouraria ---
elif st.session_state.aba_ativa == "Tesouraria":
    st.header("Parâmetros de Tesouraria")
    st.download_button("Baixar modelo", gerar_template_xlsx("tesouraria"),
                       "tesouraria.xlsx")
    arquivo_tesouraria = st.file_uploader("Importar Tesouraria", type=["xlsx"])
    if arquivo_tesouraria:
        df = pd.read_excel(arquivo_tesouraria)
        st.session_state.tesouraria = df["codigo"].tolist()
    else:
        tesouraria_input = st.text_area("Lista de tesouraria (códigos separados por vírgula)", "T001,T002")
        st.session_state.tesouraria = [x.strip() for x in tesouraria_input.split(",")]

# --- Aba Centro de Custo ---
elif st.session_state.aba_ativa == "Centro de Custo (Opcional)":
    st.header("Centro de Custo (Opcional)")
    st.download_button("📥 Baixar modelo", gerar_template_xlsx("centro_custo"),
                       "centro_custo.xlsx")
    arquivo_cc = st.file_uploader("Importar Centros de Custo", type=["xlsx"])
    if arquivo_cc:
        df = pd.read_excel(arquivo_cc)
        st.session_state.cc = df["codigo"].tolist()
    else:
        cc_input = st.text_area("Lista de centros de custo (códigos separados por vírgula)", "C001,C002")
        st.session_state.cc = [x.strip() for x in cc_input.split(",")]

# --- Aba Tipos de Documento ---
elif st.session_state.aba_ativa == "Tipos de Documento (Opcional)":
    st.header("Tipos de Documento (Opcional)")
    st.download_button("Baixar modelo", gerar_template_xlsx("tipo_doc"),
                       "tipos_documento.xlsx")
    arquivo_td = st.file_uploader("Importar Tipos de Documento", type=["xlsx"])
    if arquivo_td:
        df = pd.read_excel(arquivo_td)
        st.session_state.tipos_doc = df["codigo"].tolist()
    else:
        td_input = st.text_area("Lista de tipos de documento (códigos separados por vírgula)", "TD001,TD002")
        st.session_state.tipos_doc = [x.strip() for x in td_input.split(",")]

# --- Aba Gerar CSV ---
elif st.session_state.aba_ativa == "Gerar CSV":
    st.header("Gerar Arquivo CSV")
    num_registros = st.number_input("Número de registros", min_value=10, max_value=1000, value=100)

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

    if st.button("Gerar CSV"):
        registros = []
        for i in range(num_registros):
            tipo = random.choice(["E", "S"])
            descricao = random.choice(st.session_state.entradas if tipo == "E" else st.session_state.saidas)
            valor = random_valor()
            venc = random_date(st.session_state.data_inicio, st.session_state.data_fim)
            pagamento = random_payment_date(venc)
            venc_str = venc.strftime("%d/%m/%Y")
            pagamento_str = pagamento.strftime("%d/%m/%Y") if pagamento != "" else ""
            unidade = random.choice(st.session_state.lista_unidades)
            registros.append([i+1, tipo, valor, unidade, venc_str, pagamento_str, descricao])

        csv_file = io.StringIO()
        writer = csv.writer(csv_file)
        writer.writerow(["documento","tipo","valor","cod_unidade","data_venc","data_liq","descricao"])
        writer.writerows(registros)

        st.download_button("Baixar CSV", csv_file.getvalue(), "documentos.csv", mime="text/csv")
        st.success("CSV gerado com sucesso!")