import streamlit as st
import random
import csv
import io
import pandas as pd
from datetime import datetime, timedelta

# ---------------------------------------------
# Configuração inicial
# ---------------------------------------------
st.set_page_config(page_title="Gerador de documentos fictícios", layout="wide")
st.markdown("<h1 style='text-align:center; color:#4B8BBE;'>📄 Gerador de Documentos Fictícios (Fluxo)</h1>", unsafe_allow_html=True)

# ---------------------------------------------
# Reset de dados
# ---------------------------------------------
st.sidebar.markdown("## 🔧 Configurações")
if st.sidebar.button("🔁 Resetar todos os dados"):
    st.session_state.clear()
    st.experimental_rerun()

# ---------------------------------------------
# Inicialização do session_state
# ---------------------------------------------
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
init_state("aba_ativa", "Observações")

# ---------------------------------------------
# Funções auxiliares
# ---------------------------------------------
def gerar_template_xlsx(tipo):
    output = io.BytesIO()
    templates = {
        "entrada": {"codigo": ["E001","E002"], "nome":["Exemplo de entrada","Venda de produto"], "sheet":"entradas"},
        "saida": {"codigo": ["S001","S002"], "nome":["Exemplo de saída","Pagamento fornecedor"], "sheet":"saidas"},
        "unidades": {"codigo": ["01","02","03"], "nome":["Matriz","Filial SP","Filial RJ"], "sheet":"unidades"},
        "tesouraria": {"codigo": ["T001","T002"], "nome":["Conta Banco 1","Caixa Interno"], "sheet":"tesouraria"},
        "centro_custo": {"codigo": ["CC01","CC02"], "nome":["Administrativo","Operacional"], "sheet":"centro_custo"},
        "tipos_doc": {"codigo": ["NF","REC"], "nome":["Nota Fiscal","Recibo"], "sheet":"tipos_doc"}
    }
    if tipo in templates:
        df = pd.DataFrame({"codigo": templates[tipo]["codigo"], "nome": templates[tipo]["nome"]})
        sheet_name = templates[tipo]["sheet"]
    else:
        df = pd.DataFrame()
        sheet_name = "Sheet1"
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    output.seek(0)
    return output.getvalue()

def atualizar_lista(nome, lista_padrao, tipo_arquivo):
    with st.expander(f"🗂️ {nome}", expanded=True):
        col1, col2 = st.columns([1,1])
        lista = lista_padrao.copy()
        with col1:
            st.download_button(f"📥 Modelo {nome}", data=gerar_template_xlsx(tipo_arquivo), file_name=f"{nome}_template.xlsx")
        with col2:
            arquivo = st.file_uploader(f"Importar {nome}", type=["xlsx"], key=f"upload_{nome}")
            if arquivo:
                try:
                    df = pd.read_excel(arquivo)
                    if "codigo" in df.columns:
                        lista = df["codigo"].dropna().astype(str).tolist()
                        st.success(f"{len(lista)} {nome.lower()} importados!")
                        st.dataframe(df, use_container_width=True)
                    else:
                        st.error("Arquivo inválido: coluna 'codigo' não encontrada")
                except Exception as e:
                    st.error(f"Erro ao ler arquivo: {e}")
        entrada = st.text_area(f"{nome} (separados por vírgula)", value=",".join(lista_padrao))
        lista = [x.strip() for x in entrada.split(",") if x.strip()]
        st.session_state[f"lista_{nome.lower()}"] = lista
    return lista

def gerar_registros_csv(n):
    registros = []
    for id_counter in range(1,n+1):
        tipo = random.choice(["E","S"])
        descricao = random.choice(st.session_state.entradas_codigos if tipo=="E" else st.session_state.saidas_codigos)
        valor = round(random.uniform(1,101000),2)
        vencimento = st.session_state.data_inicio + timedelta(days=random.randint(0,(st.session_state.data_fim - st.session_state.data_inicio).days))
        pagamento = vencimento + timedelta(days=random.randint(-5,5)) if random.random()<0.5 else ""
        venc_str = vencimento.strftime("%d/%m/%Y")
        pagamento_str = pagamento.strftime("%d/%m/%Y") if pagamento != "" else ""
        cliente_fornecedor = f"C{random.randint(1,50)}" if tipo=="E" else f"F{random.randint(1,50)}"
        registros.append([
            id_counter, tipo, valor, random.choice(st.session_state.lista_unidades),
            venc_str, pagamento_str, descricao, cliente_fornecedor,
            random.choice(st.session_state.lista_tesouraria) if st.session_state.lista_tesouraria else "",
            random.choice(st.session_state.lista_cc) if st.session_state.lista_cc else "",
            random.choice(st.session_state.lista_tipos) if st.session_state.lista_tipos else ""
        ])
    return registros

# ---------------------------------------------
# Menu lateral
# ---------------------------------------------
menu_itens = [
    "Observações",
    "Período",
    "Unidades",
    "Classificações",
    "Tesouraria",
    "Centro de Custo",
    "Tipos de Documento",
    "Gerar CSV"
]
opcao = st.sidebar.radio("📂 Menu", menu_itens, index=menu_itens.index(st.session_state.aba_ativa))
st.session_state.aba_ativa = opcao

# ---------------------------------------------
# Conteúdo das abas
# ---------------------------------------------
if opcao=="Observações":
    with st.container():
        st.markdown("### 📝 Informações da função")
        st.info("""
        - Gera documentos fictícios de entradas e saídas financeiras.
        - Campos devem seguir os códigos cadastrados.
        - Período definido pelas datas inicial e final.
        - Datas de vencimento e liquidação podem ser aleatórias.
        """)

elif opcao=="Período":
    with st.expander("📅 Selecionar Período", expanded=True):
        data_inicio = st.date_input("Data inicial", value=st.session_state.data_inicio)
        data_fim = st.date_input("Data final", value=st.session_state.data_fim)
        if data_fim<data_inicio:
            st.error("A data final não pode ser menor que a inicial!")
        st.session_state.data_inicio = data_inicio
        st.session_state.data_fim = data_fim

elif opcao=="Unidades":
    atualizar_lista("Unidades", st.session_state.lista_unidades, "unidades")

elif opcao=="Classificações":
    atualizar_lista("Entradas", st.session_state.entradas_codigos, "entrada")
    atualizar_lista("Saídas", st.session_state.saidas_codigos, "saida")

elif opcao=="Tesouraria":
    atualizar_lista("Tesouraria", st.session_state.lista_tesouraria, "tesouraria")

elif opcao=="Centro de Custo":
    atualizar_lista("Centro de Custo", st.session_state.lista_cc, "centro_custo")

elif opcao=="Tipos de Documento":
    atualizar_lista("Tipos de Documento", st.session_state.lista_tipos, "tipos_doc")

elif opcao=="Gerar CSV":
    with st.expander("💾 Gerar Arquivo CSV", expanded=True):
        num_registros = st.number_input("Número de registros", min_value=10, max_value=1000, value=100)
        if st.button("🟢 Gerar CSV"):
            registros = gerar_registros_csv(num_registros)
            csv_buffer = io.StringIO()
            writer = csv.writer(csv_buffer)
            writer.writerow([
                "documento","tipo","valor","cod_unidade","data_venc","data_liq",
                "descricao","cliente_fornecedor","tesouraria","centro_custo","tipo_documento"
            ])
            writer.writerows(registros)
            csv_buffer.seek(0)
            st.success(f"CSV gerado com {len(registros)} registros!")
            st.download_button("📥 Download CSV", data=csv_buffer, file_name="documentos.csv", mime="text/csv")