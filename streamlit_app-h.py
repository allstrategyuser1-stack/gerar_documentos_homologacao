import streamlit as st
import pandas as pd
import random
import csv
import io
from datetime import datetime, timedelta

# ---------------------------
# Configuração inicial
# ---------------------------
st.set_page_config(page_title="Gerador de documentos fictícios (Fluxo)", layout="wide")
st.title("Gerador de documentos fictícios (Fluxo) (v2.0.0)")

# ---------------------------
# Função para inicializar session_state
# ---------------------------
def init_state(key, default):
    if key not in st.session_state:
        st.session_state[key] = default

init_state("data_inicio", datetime(2025, 1, 1))
init_state("data_fim", datetime(2025, 12, 31))
init_state("lista_unidades", ["01", "02", "03"])
init_state("entradas_codigos", ["E001", "E002"])
init_state("saidas_codigos", ["S001", "S002"])
init_state("lista_tesouraria", ["T001", "T002"])
init_state("lista_cc", ["CC01", "CC02"])
init_state("lista_tipos", ["NF", "REC"])
init_state("aba_ativa", "Observações da função")

# ---------------------------
# Função para gerar templates XLSX
# ---------------------------
def gerar_template(tipo):
    templates = {
        "entrada": {"codigo": ["E001","E002"], "nome": ["Exemplo","Venda"]},
        "saida": {"codigo": ["S001","S002"], "nome": ["Exemplo","Pagamento"]},
        "unidades": {"codigo": ["01","02","03"], "nome": ["Matriz","Filial SP","Filial RJ"]},
        "tesouraria": {"codigo": ["T001","T002"], "nome": ["Banco 1","Caixa"]},
        "centro_custo": {"codigo": ["CC01","CC02"], "nome": ["Adm","Oper"]},
        "tipos_doc": {"codigo": ["NF","REC"], "nome": ["Nota Fiscal","Recibo"]}
    }
    df = pd.DataFrame(templates.get(tipo, {}))
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=tipo)
    output.seek(0)
    return output.getvalue()

# ---------------------------
# CSS Menu lateral
# ---------------------------
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
    cursor: pointer;
    text-align: left;
    display: block;
    width: 100%;
    box-sizing: border-box;
}
.menu-botao:hover { background-color: #ffe082; }
.menu-ativo { background-color: #FFD700 !important; color: black !important; font-weight: 700 !important; border: 1px solid #d4af37; }
</style>
""", unsafe_allow_html=True)

# ---------------------------
# Menu lateral
# ---------------------------
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

for item in menu_itens:
    if item == st.session_state.aba_ativa:
        st.sidebar.markdown(f"<div class='menu-botao menu-ativo'>{item}</div>", unsafe_allow_html=True)
    else:
        if st.sidebar.button(item):
            st.session_state.aba_ativa = item
            st.experimental_rerun()

opcao = st.session_state.aba_ativa

# ---------------------------
# Função genérica para abas de templates
# ---------------------------
def aba_template(nome, tipo_template, session_key):
    st.header(nome)
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(f"📥 Baixar modelo {nome}", data=gerar_template(tipo_template), file_name=f"{tipo_template}_template.xlsx")
    with col2:
        arquivo = st.file_uploader(f"Importar {nome}", type=["xlsx"])
    if arquivo:
        df = pd.read_excel(arquivo)
        if "codigo" in df.columns:
            lista = df["codigo"].dropna().astype(str).tolist()
            st.session_state[session_key] = lista
            st.success(f"{len(lista)} {nome} importados")
            st.dataframe(df, use_container_width=True)
    else:
        input_text = st.text_area(f"{nome} (separados por vírgula)", value=",".join(st.session_state[session_key]))
        st.session_state[session_key] = [x.strip() for x in input_text.split(",") if x.strip()]

# ---------------------------
# Abas
# ---------------------------
if opcao == "Observações da função":
    st.markdown("""
    <div style="text-align: justify; font-size:18px; border:1px solid #ddd; border-radius:10px; padding:15px; background-color:#f9f9f9;">
        <h3 style="text-align:center; color:#333;">Observações sobre a função</h3>
        <ul>
            <li>Gera documentos fictícios de entradas e saídas financeiras.</li>
            <li>O campo de unidade deve ser preenchido com os códigos cadastrados no Fluxo.</li>
            <li>Classificações podem ser preenchidas via template ou manualmente.</li>
            <li>O período de geração é determinado pelas datas inicial e final.</li>
            <li>Datas identificam vencimento; liquidação pode ser aleatória.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

elif opcao == "Período":
    st.header("Selecionar período dos registros")
    col1, col2 = st.columns(2)
    with col1:
        data_inicio_str = st.text_input("Data inicial (dd/mm/aaaa)", value=st.session_state.data_inicio.strftime("%d/%m/%Y"))
        try: st.session_state.data_inicio = datetime.strptime(data_inicio_str, "%d/%m/%Y")
        except: st.error("Formato inválido!")
    with col2:
        data_fim_str = st.text_input("Data final (dd/mm/aaaa)", value=st.session_state.data_fim.strftime("%d/%m/%Y"))
        try: st.session_state.data_fim = datetime.strptime(data_fim_str, "%d/%m/%Y")
        except: st.error("Formato inválido!")

elif opcao == "Unidades":
    aba_template("Unidades", "unidades", "lista_unidades")

elif opcao == "Classificações":
    st.subheader("Entradas")
    aba_template("Entradas", "entrada", "entradas_codigos")
    st.subheader("Saídas")
    aba_template("Saídas", "saida", "saidas_codigos")

elif opcao == "Tesouraria":
    aba_template("Tesouraria", "tesouraria", "lista_tesouraria")

elif opcao == "Centro de Custo (Opcional)":
    aba_template("Centro de Custo", "centro_custo", "lista_cc")

elif opcao == "Tipos de Documento (Opcional)":
    aba_template("Tipos de Documento", "tipos_doc", "lista_tipos")

elif opcao == "Gerar CSV":
    st.header("Gerar Arquivo CSV")
    num_registros = st.number_input("Número de registros", min_value=10, max_value=1000, value=100)
    
    def random_date(start, end):
        delta = end - start
        return start + timedelta(days=random.randint(0, delta.days))
    
    def random_payment_date(due_date):
        return due_date + timedelta(days=random.randint(-5,5)) if random.random()<0.5 else ""
    
    def random_valor():
        return round(random.uniform(1,101000),2)

    if st.button("Gerar CSV"):
        registros=[]
        for i in range(1,num_registros+1):
            tipo=random.choice(["E","S"])
            descricao=random.choice(st.session_state.entradas_codigos if tipo=="E" else st.session_state.saidas_codigos)
            valor=random_valor()
            vencimento=random_date(st.session_state.data_inicio, st.session_state.data_fim)
            pagamento=random_payment_date(vencimento)
            registros.append([
                i,tipo,valor,random.choice(st.session_state.lista_unidades),
                vencimento.strftime("%d/%m/%Y"), pagamento.strftime("%d/%m/%Y") if pagamento!="" else "",
                descricao,f"C{random.randint(1,50)}" if tipo=="E" else f"F{random.randint(1,50)}",
                random.choice(st.session_state.lista_tesouraria), random.choice(st.session_state.lista_cc), random.choice(st.session_state.lista_tipos)
            ])
        csv_file="documentos.csv"
        with open(csv_file,"w",newline="",encoding="utf-8-sig") as f:
            writer=csv.writer(f)
            writer.writerow(["documento","tipo","valor","cod_unidade","data_venc","data_liq","descricao","cliente_fornecedor","tesouraria","centro_custo","tipo_documento"])
            writer.writerows(registros)
        st.success(f"CSV gerado com {len(registros)} registros!")
        st.download_button("📥 Download CSV", open(csv_file,"rb"), file_name="documentos.csv")