import streamlit as st
import random
import csv
from datetime import datetime, timedelta
import pandas as pd
import io

st.set_page_config(page_title="Gerador de documentos fictícios (Fluxo)", layout="wide")
st.title("Gerador de documentos fictícios (Fluxo) (v2.0.0)")

# --- Função para gerar templates XLSX ---
def gerar_template_xlsx(tipo):
    output = io.BytesIO()
    if tipo == "entrada":
        df = pd.DataFrame({
            "codigo": ["E001", "E002"],
            "nome": ["Exemplo de entrada", "Venda de produto"]
        })
        sheet_name = "classificacoes_entrada"

    elif tipo == "saida":
        df = pd.DataFrame({
            "codigo": ["S001", "S002"],
            "nome": ["Exemplo de saída", "Pagamento de fornecedor"]
        })
        sheet_name = "classificacoes_saida"

    elif tipo == "unidades":
        df = pd.DataFrame({
            "codigo": ["01", "02", "03"],
            "nome": ["Matriz", "Filial SP", "Filial RJ"]
        })
        sheet_name = "unidades"

    elif tipo == "tesouraria":
        df = pd.DataFrame({
            "codigo": ["T001", "T002"],
            "nome": ["Conta Banco 1", "Caixa Interno"]
        })
        sheet_name = "tesouraria"

    elif tipo == "centro_custo":
        df = pd.DataFrame({
            "codigo": ["CC01", "CC02"],
            "nome": ["Administrativo", "Operacional"]
        })
        sheet_name = "centro_custo"

    elif tipo == "tipos_doc":
        df = pd.DataFrame({
            "codigo": ["NF", "REC"],
            "nome": ["Nota Fiscal", "Recibo"]
        })
        sheet_name = "tipos_documento"

    else:
        df = pd.DataFrame()
        sheet_name = "Sheet1"

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    output.seek(0)
    return output.getvalue()


# --- Menu lateral simulando abas ---
opcao = st.sidebar.radio("Seções", [
    "Observações da função",
    "Período",
    "Unidades",
    "Classificações",
    "Tesouraria",
    "Centro de Custo (Opcional)",
    "Tipos de Documento (Opcional)",
    "Gerar CSV"
])

# ============================
# --- Observações ---
# ============================
if opcao == "Observações da função":
    st.markdown("""
    <div style="
        text-align: justify;
        font-size:18px;
        border:1px solid #ddd;
        border-radius:10px;
        padding:15px;
        background-color:#f9f9f9;">
        <h3 style="text-align:center; color:#333;">Observações sobre a função</h3>
        <ul>
            <li>A função gera documentos fictícios de entradas e saídas financeiras com base nos parâmetros definidos.</li>
            <li>O campo de unidade deve ser preenchido com os códigos cadastrados no Fluxo e as unidades identificadas serão utilizadas de forma aleatória para cada documento.</li>
            <li>O campo de classificações deve ser preenchido com os códigos <b>externos</b> cadastrados no Fluxo e as classificações podem ser importadas via arquivos CSV ou informadas manualmente e também serão utilizadas de forma aleatória.</li>
            <li>O período de geração é determinado pelas datas inicial e final informadas.</li>
            <li>As datas informadas identificam o período de <b>vencimento</b> dos documentos, a data de liquidação é aleatória e alguns documentos terão a data de liquidação em branco para simular atrasados ou previstos.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# ============================
# --- Período ---
# ============================
elif opcao == "Período":
    st.header("Selecionar período dos registros")
    col1, col2 = st.columns(2)
    with col1:
        data_inicio_str = st.text_input("Data inicial (dd/mm/aaaa)", value="01/01/2025")
        try:
            data_inicio = datetime.strptime(data_inicio_str, "%d/%m/%Y")
        except:
            st.error("Formato de data inicial inválido! Use dd/mm/aaaa")
            st.stop()
    with col2:
        data_fim_str = st.text_input("Data final (dd/mm/aaaa)", value="31/12/2025")
        try:
            data_fim = datetime.strptime(data_fim_str, "%d/%m/%Y")
        except:
            st.error("Formato de data final inválido! Use dd/mm/aaaa")
            st.stop()

# ============================
# --- Unidades ---
# ============================
elif opcao == "Unidades":
    st.header("Identificação de Unidades")
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="📥 Baixar modelo de Unidades (XLSX)",
            data=gerar_template_xlsx("unidades"),
            file_name="unidades_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    with col2:
        arquivo_unidades = st.file_uploader("Importar arquivo de Unidades", type=["xlsx"])

    lista_unidades = []
    if arquivo_unidades:
        df_unidades = pd.read_excel(arquivo_unidades)
        lista_unidades = df_unidades["codigo"].dropna().astype(str).tolist()
        st.success(f"{len(lista_unidades)} unidades importadas.")
    else:
        unidades_input = st.text_area("Lista de unidades (separadas por vírgula)", value="")
        lista_unidades = [u.strip() for u in unidades_input.split(",") if u.strip()]

# ============================
# --- Classificações ---
# ============================
elif opcao == "Classificações":
    st.header("Importar Classificações")
    col_esq, col_vline, col_dir = st.columns([48, 1, 48])
    with col_esq:
        st.subheader("Entradas")
        st.download_button(
            label="📥 Baixar modelo de Entradas",
            data=gerar_template_xlsx("entrada"),
            file_name="classificacoes_entrada.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        arquivo_entradas = st.file_uploader("Importar lista de classificações de Entrada", type=["xlsx"])
    col_vline.markdown("""<div style="border-left:2px solid #CCC; height:240px; margin-left:50%;"></div>""",
                       unsafe_allow_html=True)
    with col_dir:
        st.subheader("Saídas")
        st.download_button(
            label="📥 Baixar modelo de Saídas",
            data=gerar_template_xlsx("saida"),
            file_name="classificacoes_saida.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        arquivo_saidas = st.file_uploader("Importar lista de classificações de Saída", type=["xlsx"])

    entradas_codigos, saidas_codigos = [], []
    if arquivo_entradas is not None:
        df_entradas = pd.read_excel(arquivo_entradas)
        entradas_codigos = df_entradas["codigo"].dropna().astype(str).tolist()
    if arquivo_saidas is not None:
        df_saidas = pd.read_excel(arquivo_saidas)
        saidas_codigos = df_saidas["codigo"].dropna().astype(str).tolist()
    if not entradas_codigos:
        entradas_input = st.text_area("Classificações de Entrada (separadas por vírgula)", value="")
        entradas_codigos = [e.strip() for e in entradas_input.split(",") if e.strip()]
    if not saidas_codigos:
        saidas_input = st.text_area("Classificações de Saída (separadas por vírgula)", value="")
        saidas_codigos = [s.strip() for s in saidas_input.split(",") if s.strip()]

# ============================
# --- Tesouraria ---
# ============================
elif opcao == "Tesouraria":
    st.header("Identificação da Tesouraria")
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="📥 Baixar modelo de Tesouraria",
            data=gerar_template_xlsx("tesouraria"),
            file_name="tesouraria_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    with col2:
        arquivo_tesouraria = st.file_uploader("Importar Tesouraria", type=["xlsx"])

    lista_tesouraria = []
    if arquivo_tesouraria:
        df_tes = pd.read_excel(arquivo_tesouraria)
        lista_tesouraria = df_tes["codigo"].dropna().astype(str).tolist()
        st.success(f"{len(lista_tesouraria)} contas de tesouraria importadas.")
    else:
        tes_input = st.text_area("Contas de Tesouraria (separadas por vírgula)", value="")
        lista_tesouraria = [t.strip() for t in tes_input.split(",") if t.strip()]

# ============================
# --- Centro de Custo ---
# ============================
elif opcao == "Centro de Custo (Opcional)":
    st.header("Centro de Custo (Opcional)")
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="📥 Baixar modelo de Centro de Custo",
            data=gerar_template_xlsx("centro_custo"),
            file_name="centro_custo_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    with col2:
        arquivo_cc = st.file_uploader("Importar Centro de Custo", type=["xlsx"])

    lista_cc = []
    if arquivo_cc:
        df_cc = pd.read_excel(arquivo_cc)
        lista_cc = df_cc["codigo"].dropna().astype(str).tolist()
        st.success(f"{len(lista_cc)} centros de custo importados.")
    else:
        cc_input = st.text_area("Centros de Custo (separados por vírgula)", value="")
        lista_cc = [c.strip() for c in cc_input.split(",") if c.strip()]

# ============================
# --- Tipos de Documento ---
# ============================
elif opcao == "Tipos de Documento (Opcional)":
    st.header("Tipos de Documento (Opcional)")
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="📥 Baixar modelo de Tipos de Documento",
            data=gerar_template_xlsx("tipos_doc"),
            file_name="tipos_documento_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    with col2:
        arquivo_tipos = st.file_uploader("Importar Tipos de Documento", type=["xlsx"])

    lista_tipos = []
    if arquivo_tipos:
        df_tipos = pd.read_excel(arquivo_tipos)
        lista_tipos = df_tipos["codigo"].dropna().astype(str).tolist()
        st.success(f"{len(lista_tipos)} tipos de documento importados.")
    else:
        tipos_input = st.text_area("Tipos de Documento (separados por vírgula)", value="")
        lista_tipos = [t.strip() for t in tipos_input.split(",") if t.strip()]

# ============================
# --- Gerar CSV ---
# ============================
elif opcao == "Gerar CSV":
    st.header("Gerar Arquivo CSV")
    num_registros = st.number_input("Número de registros", min_value=10, max_value=1000, value=100)

    # Funções auxiliares
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

    registros = []
    id_counter = 1

    if st.button("Gerar CSV"):
        while len(registros) < num_registros:
            tipo = random.choice(["E", "S"])
            descricao = random.choice(entradas_codigos) if tipo == "E" else random.choice(saidas_codigos)
            valor = random_valor()
            vencimento = random_date(data_inicio, data_fim)
            pagamento = random_payment_date(vencimento)
            venc_str = vencimento.strftime("%d/%m/%Y")
            pagamento_str = pagamento.strftime("%d/%m/%Y") if pagamento != "" else ""
            cliente_fornecedor = f"C{random.randint(1,50)}" if tipo == "E" else f"F{random.randint(1,50)}"
            cod_unidade = random.choice(lista_unidades)
            tes = random.choice(lista_tesouraria) if lista_tesouraria else ""
            cc = random.choice(lista_cc) if lista_cc else ""
            tipo_doc = random.choice(lista_tipos) if lista_tipos else ""

            registros.append([
                id_counter, tipo, valor, cod_unidade, venc_str, pagamento_str,
                descricao, cliente_fornecedor, tes, cc, tipo_doc
            ])
            id_counter += 1

        # Criar CSV
        csv_file = "documentos.csv"
        with open(csv_file, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow([
                "documento", "tipo", "valor", "cod_unidade", "data_venc",
                "data_liq", "descricao", "cliente_fornecedor",
                "tesouraria", "centro_custo", "tipo_documento"
            ])
            writer.writerows(registros)

        st.success(f"CSV gerado com {len(registros)} registros!")
        st.download_button("📄 Download do arquivo gerado",
                           open(csv_file, "rb"),
                           file_name="documentos.csv")