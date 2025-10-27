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
.sidebar-container button[kind="secondary"] {
    width: 100% !important;
    border-radius: 6px;
    border: 1px solid #dcdcdc !important;
    color: #333 !important;
    font-weight: 500 !important;
    margin-bottom: 6px;
    text-align: center !important;
    background-color: #f2f2f2 !important;
}
.sidebar-container button[kind="secondary"]:hover {
    background-color: #ffe082 !important;
    border-color: #d4af37 !important;
}
.sidebar-container .active-btn {
    background-color: #FFD700 !important;
    color: black !important;
    font-weight: 700 !important;
    border: 1px solid #d4af37 !important;
}
</style>
""", unsafe_allow_html=True)

# --- Abas ---
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

# --- Função de menu lateral (sem duplicar conteúdo) ---
with st.sidebar:
    st.markdown("<div class='sidebar-container'>", unsafe_allow_html=True)
    st.title("📂 Menu de Abas")

    for aba in abas:
        btn_key = f"btn_{aba}"
        # Detecta se esta é a aba ativa
        is_active = (st.session_state.aba_ativa == aba)
        if st.button(aba, key=btn_key):
            st.session_state.aba_ativa = aba
        # Mantém o botão ativo em destaque
        if is_active:
            st.markdown(f"<script>document.querySelector('button[key=\"{btn_key}\"]').classList.add('active-btn')</script>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# --- Função para gerar templates XLSX ---
def gerar_template_xlsx(tipo):
    output = io.BytesIO()
    exemplos = {
        "entrada": ["E001", "E002"],
        "saida": ["S001", "S002"],
        "tesouraria": ["T001", "T002"],
        "centro_custo": ["CC001", "CC002"],
        "tipo_doc": ["TD001", "TD002"],
        "unidades": ["U001", "U002"],
    }
    df = pd.DataFrame({"codigo": exemplos.get(tipo, [])})
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=tipo)
    output.seek(0)
    return output.getvalue()

# ======================================================
# CONTEÚDO DAS ABAS
# ======================================================

st.title(f"📘 {st.session_state.aba_ativa}")

# --- Aba 1: Observações ---
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

# --- Aba 2: Período ---
elif st.session_state.aba_ativa == "Período":
    st.header("Selecionar Período dos Registros")
    col1, col2 = st.columns(2)
    with col1:
        data_inicio_str = st.text_input("Data inicial (dd/mm/aaaa)", value=st.session_state.get("data_inicio_str", "01/01/2025"))
        st.session_state.data_inicio_str = data_inicio_str
        try:
            st.session_state.data_inicio = datetime.strptime(data_inicio_str, "%d/%m/%Y")
        except:
            st.error("Formato inválido! Use dd/mm/aaaa")
    with col2:
        data_fim_str = st.text_input("Data final (dd/mm/aaaa)", value=st.session_state.get("data_fim_str", "31/12/2025"))
        st.session_state.data_fim_str = data_fim_str
        try:
            st.session_state.data_fim = datetime.strptime(data_fim_str, "%d/%m/%Y")
        except:
            st.error("Formato inválido! Use dd/mm/aaaa")

# --- Aba 3: Unidades ---
elif st.session_state.aba_ativa == "Unidades":
    st.header("Identificação de Unidades")
    col1, col2 = st.columns(2)
    with col1:
        st.download_button("📥 Baixar modelo de Unidades (XLSX)", gerar_template_xlsx("unidades"),
                           file_name="unidades_template.xlsx")
    with col2:
        arquivo_unidades = st.file_uploader("Importar arquivo de Unidades", type=["xlsx"])

    if arquivo_unidades:
        df_unidades = pd.read_excel(arquivo_unidades)
        st.session_state.lista_unidades = df_unidades["codigo"].dropna().astype(str).tolist()
        st.success(f"{len(st.session_state.lista_unidades)} unidades importadas.")
    else:
        unidades_input = st.text_area("Lista de unidades (separadas por vírgula)", value="U001,U002")
        st.session_state.lista_unidades = [u.strip() for u in unidades_input.split(",") if u.strip()]

# --- Aba 4: Classificações ---
elif st.session_state.aba_ativa == "Classificações":
    st.header("Importar Classificações")
    col_esq, col_dir = st.columns(2)
    with col_esq:
        st.subheader("Entradas")
        st.download_button("📥 Baixar modelo de Entradas", gerar_template_xlsx("entrada"), "classificacoes_entrada.xlsx")
        arquivo_entradas = st.file_uploader("Importar lista de classificações de Entrada", type=["xlsx"])
        if arquivo_entradas:
            df = pd.read_excel(arquivo_entradas)
            st.session_state.entradas_codigos = df["codigo"].dropna().astype(str).tolist()
        else:
            entradas_input = st.text_area("Classificações de Entrada (separadas por vírgula)", "E001,E002")
            st.session_state.entradas_codigos = [x.strip() for x in entradas_input.split(",") if x.strip()]
    with col_dir:
        st.subheader("Saídas")
        st.download_button("📥 Baixar modelo de Saídas", gerar_template_xlsx("saida"), "classificacoes_saida.xlsx")
        arquivo_saidas = st.file_uploader("Importar lista de classificações de Saída", type=["xlsx"])
        if arquivo_saidas:
            df = pd.read_excel(arquivo_saidas)
            st.session_state.saidas_codigos = df["codigo"].dropna().astype(str).tolist()
        else:
            saidas_input = st.text_area("Classificações de Saída (separadas por vírgula)", "S001,S002")
            st.session_state.saidas_codigos = [x.strip() for x in saidas_input.split(",") if x.strip()]

# --- Aba 5: Tesouraria ---
elif st.session_state.aba_ativa == "Tesouraria":
    st.header("Identificação da Tesouraria")
    st.download_button("📥 Baixar modelo", gerar_template_xlsx("tesouraria"), "tesouraria.xlsx")
    arquivo_tes = st.file_uploader("Importar Tesouraria", type=["xlsx"])
    if arquivo_tes:
        df = pd.read_excel(arquivo_tes)
        st.session_state.tesouraria = df["codigo"].dropna().astype(str).tolist()
        st.success(f"{len(st.session_state.tesouraria)} contas importadas.")
    else:
        tes_input = st.text_area("Contas de Tesouraria (separadas por vírgula)", "T001,T002")
        st.session_state.tesouraria = [x.strip() for x in tes_input.split(",") if x.strip()]

# --- Aba 6: Centro de Custo ---
elif st.session_state.aba_ativa == "Centro de Custo (Opcional)":
    st.header("Centro de Custo (Opcional)")
    st.download_button("📥 Baixar modelo", gerar_template_xlsx("centro_custo"), "centro_custo.xlsx")
    arquivo_cc = st.file_uploader("Importar Centro de Custo", type=["xlsx"])
    if arquivo_cc:
        df = pd.read_excel(arquivo_cc)
        st.session_state.cc = df["codigo"].dropna().astype(str).tolist()
    else:
        cc_input = st.text_area("Centros de Custo (separados por vírgula)", "CC001,CC002")
        st.session_state.cc = [x.strip() for x in cc_input.split(",") if x.strip()]

# --- Aba 7: Tipos de Documento ---
elif st.session_state.aba_ativa == "Tipos de Documento (Opcional)":
    st.header("Tipos de Documento (Opcional)")
    st.download_button("📥 Baixar modelo", gerar_template_xlsx("tipo_doc"), "tipo_doc.xlsx")
    arquivo_td = st.file_uploader("Importar Tipos de Documento", type=["xlsx"])
    if arquivo_td:
        df = pd.read_excel(arquivo_td)
        st.session_state.tipos_doc = df["codigo"].dropna().astype(str).tolist()
    else:
        td_input = st.text_area("Tipos de Documento (separados por vírgula)", "TD001,TD002")
        st.session_state.tipos_doc = [x.strip() for x in td_input.split(",") if x.strip()]

# --- Aba 8: Gerar CSV ---
elif st.session_state.aba_ativa == "Gerar CSV":
    st.header("Gerar Arquivo CSV")
    num_registros = st.number_input("Número de registros", min_value=10, max_value=1000, value=100)

    def random_date(start, end):
        delta = end - start
        return start + timedelta(days=random.randint(0, delta.days))

    def random_payment_date(due_date):
        return due_date + timedelta(days=random.randint(-5, 5)) if random.random() < 0.5 else ""

    def random_valor():
        return round(random.uniform(10, 10000), 2)

    if st.button("Gerar CSV"):
        registros = []
        for i in range(num_registros):
            tipo = random.choice(["E", "S"])
            descricao = random.choice(
                st.session_state.get("entradas_codigos", ["E001"]) if tipo == "E" else
                st.session_state.get("saidas_codigos", ["S001"])
            )
            valor = random_valor()
            venc = random_date(st.session_state.data_inicio, st.session_state.data_fim)
            pagamento = random_payment_date(venc)
            venc_str = venc.strftime("%d/%m/%Y")
            pagamento_str = pagamento.strftime("%d/%m/%Y") if pagamento != "" else ""
            unidade = random.choice(st.session_state.get("lista_unidades", ["U001"]))
            registros.append([i+1, tipo, valor, unidade, venc_str, pagamento_str, descricao])

        csv_file = io.StringIO()
        writer = csv.writer(csv_file)
        writer.writerow(["documento","tipo","valor","cod_unidade","data_venc","data_liq","descricao"])
        writer.writerows(registros)

        st.download_button("📤 Baixar CSV Gerado", csv_file.getvalue(), "documentos.csv", mime="text/csv")
        st.success("✅ CSV gerado com sucesso!")