import streamlit as st
import random
import csv
from datetime import datetime, timedelta
import pandas as pd
import io

st.set_page_config(page_title="Gerador de documentos fictícios (Fluxo)", layout="wide")
st.title("Gerador de documentos fictícios (Fluxo) (v1.0.0)")

# --- Função para gerar templates XLSX ---
def gerar_template_xlsx(tipo):
    output = io.BytesIO()
    if tipo == "entrada":
        df = pd.DataFrame({"codigo": ["E001", "E002"], "nome": ["Exemplo de entrada", "Venda de produto"]})
    else:
        df = pd.DataFrame({"codigo": ["S001", "S002"], "nome": ["Exemplo de saída", "Pagamento de fornecedor"]})
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="classificacoes")
    output.seek(0)
    return output.getvalue()

# --- Cria as abas ---
aba_periodo, aba_unidades, aba_classificacoes, aba_gerar = st.tabs([
    "Período", "Unidades", "Classificações", "Gerar CSV"
])

# --- Aba Período ---
with aba_periodo:
    st.header("Selecionar Período dos Registros")
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

# --- Aba Unidades ---
with aba_unidades:
    st.header("Identificação de Unidades")
    unidades_input = st.text_area("Lista de unidades (separadas por vírgula)", value="01,02,03")
    lista_unidades = [u.strip() for u in unidades_input.split(",") if u.strip()]

# --- Aba Classificações ---
with aba_classificacoes:
    st.header("Importar Classificações")
    col_esq, col_vline, col_dir = st.columns([48, 1, 48])

    with col_esq:
        st.subheader("Entradas")
        st.download_button(
            label="Baixar modelo (XLSX)",
            data=gerar_template_xlsx("entrada"),
            file_name="classificacoes_de_entrada.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        arquivo_entradas = st.file_uploader("Importar lista de classificações de Entrada", type=["xlsx"])
    
    # linha vertical
    vline_html = """<div style="border-left:2px solid #CCC; height:240px; margin-left:50%;"></div>"""
    col_vline.markdown(vline_html, unsafe_allow_html=True)
    
    with col_dir:
        st.subheader("Saídas")
        st.download_button(
            label="Baixar modelo (XLSX)",
            data=gerar_template_xlsx("saida"),
            file_name="classificacoes_de_saida.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        arquivo_saidas = st.file_uploader("Importar lista de classificações de Saída", type=["xlsx"])

    # Leitura das classificações importadas ou digitadas manualmente
    entradas_codigos, saidas_codigos = [], []
    
    if 'arquivo_entradas' in locals() and arquivo_entradas is not None:
        df_entradas = pd.read_excel(arquivo_entradas)
        entradas_codigos = df_entradas["codigo"].dropna().astype(str).tolist()
    
    if 'arquivo_saidas' in locals() and arquivo_saidas is not None:
        df_saidas = pd.read_excel(arquivo_saidas)
        saidas_codigos = df_saidas["codigo"].dropna().astype(str).tolist()
    
    # Caso não tenha upload, permitir digitação manual
    if not entradas_codigos:
        entradas_input = st.text_area("Lista de classificações de Entrada (separadas por vírgula)", value="E001,E002,E003")
        entradas_codigos = [e.strip() for e in entradas_input.split(",") if e.strip()]
    
    if not saidas_codigos:
        saidas_input = st.text_area("Lista de classificações de Saída (separadas por vírgula)", value="S001,S002,S003")
        saidas_codigos = [s.strip() for s in saidas_input.split(",") if s.strip()]

# --- Aba Gerar CSV ---
with aba_gerar:
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
            registros.append([id_counter, tipo, valor, cod_unidade, venc_str, pagamento_str, descricao, cliente_fornecedor])
            id_counter += 1

        # Criar CSV
        csv_file = "documentos.csv"
        with open(csv_file, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["documento","tipo","valor","cod_unidade","data_venc","data_liq","descricao","cliente_fornecedor"])
            writer.writerows(registros)
        
        st.success(f"CSV gerado com {len(registros)} registros!")
        st.download_button("Download do arquivo gerado", open(csv_file, "rb"), file_name="documentos.csv")