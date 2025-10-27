import streamlit as st
import random
import io
import pandas as pd
from datetime import datetime, timedelta

# -------------------------------------------------
# ⚙️ CONFIGURAÇÃO INICIAL
# -------------------------------------------------
st.set_page_config(page_title="Gerador de documentos fictícios", layout="wide")
st.markdown("<h1 style='text-align:center; color:#5a7be0;'>Gerador de Documentos Fictícios (Fluxo)</h1>", unsafe_allow_html=True)

# -------------------------------------------------
# 🧩 ESTADO INICIAL
# -------------------------------------------------
DEFAULT_STATE = {
    "step": 0,
    "data_inicio": datetime(2025, 1, 1),
    "data_fim": datetime(2025, 12, 31),
    "lista_unidades": ["01", "02", "03"],
    "entradas_codigos": ["E001", "E002"],
    "saidas_codigos": ["S001", "S002"],
    "lista_tesouraria": ["T001", "T002"],
    "lista_cc": ["CC01", "CC02"],
    "lista_tipos": ["NF", "REC"],
    "registros_gerados": [],
    "csv_gerado": False
}
for k, v in DEFAULT_STATE.items():
    st.session_state.setdefault(k, v)

# -------------------------------------------------
# 🎨 CSS GLOBAL
# -------------------------------------------------
st.markdown("""
<style>
div.stButton > button {
    background-color: #fff59d !important;
    color: black !important;
    font-weight: bold;
    border-radius: 8px;
    padding: 0.5em 1em;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# 🧠 FUNÇÕES AUXILIARES
# -------------------------------------------------
TEMPLATES = {
    "entrada": ("entradas", ["E001", "E002"], ["Exemplo de entrada", "Venda de produto"]),
    "saida": ("saidas", ["S001", "S002"], ["Exemplo de saída", "Pagamento fornecedor"]),
    "unidades": ("unidades", ["01", "02", "03"], ["Matriz", "Filial SP", "Filial RJ"]),
    "tesouraria": ("tesouraria", ["T001", "T002"], ["Conta Banco 1", "Caixa Interno"]),
    "centro_custo": ("centro_custo", ["CC01", "CC02"], ["Administrativo", "Operacional"]),
    "tipos_doc": ("tipos_doc", ["NF", "REC"], ["Nota Fiscal", "Recibo"])
}

def gerar_template_xlsx(tipo):
    output = io.BytesIO()
    sheet, codigos, nomes = TEMPLATES.get(tipo, ("Sheet1", [], []))
    df = pd.DataFrame({"codigo": codigos, "nome": nomes})
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet)
    output.seek(0)
    return output.getvalue()

def ler_codigos_excel(arquivo):
    try:
        df = pd.read_excel(arquivo)
        if "codigo" in df.columns:
            lista = df["codigo"].dropna().astype(str).tolist()
            st.success(f"{len(lista)} itens importados!")
            st.dataframe(df, use_container_width=True)
            return lista
        else:
            st.error("Coluna 'codigo' não encontrada.")
    except Exception as e:
        st.error(f"Erro ao ler arquivo: {e}")
    return []

def atualizar_lista(nome, lista_padrao, tipo_arquivo, key):
    st.markdown(f"### {nome}")
    lista = lista_padrao.copy()
    col1, col2 = st.columns(2)
    with col1:
        st.download_button("📥 Modelo", data=gerar_template_xlsx(tipo_arquivo),
                           file_name=f"{nome}_template.xlsx", key=f"dl_{nome}")
    with col2:
        arquivo = st.file_uploader(f"Importar {nome}", type=["xlsx"], key=f"upload_{key}")
        if arquivo:
            lista = ler_codigos_excel(arquivo) or lista

    lista_text = st.text_area(f"{nome} (separados por vírgula)",
                              value=",".join(lista), height=60)
    lista = [x.strip() for x in lista_text.split(",") if x.strip()]
    st.session_state[f"lista_{key}"] = lista
    return bool(lista)

def gerar_registros_csv(n):
    data_inicio, data_fim = st.session_state.data_inicio, st.session_state.data_fim
    dias_range = (data_fim - data_inicio).days

    tipos = [random.choice(["E", "S"]) for _ in range(n)]
    valores = [round(random.uniform(1, 101000), 2) for _ in range(n)]
    vencimentos = [data_inicio + timedelta(days=random.randint(0, dias_range)) for _ in range(n)]

    def pagamento_aleatorio(v):
        if random.random() < 0.5:
            p = v + timedelta(days=random.randint(-5, 5))
            return max(min(p, datetime.today()), data_inicio)
        return None

    pagamentos = [pagamento_aleatorio(v) for v in vencimentos]
    def escolha(lista): return random.choice(lista) if lista else ""

    registros = pd.DataFrame({
        "id": range(1, n+1),
        "natureza": tipos,
        "valor": valores,
        "unidade": [escolha(st.session_state.lista_unidades) for _ in range(n)],
        "vencimento": [v.strftime("%d/%m/%Y") for v in vencimentos],
        "pagamento": [p.strftime("%d/%m/%Y") if p else "" for p in pagamentos],
        "descricao": [
            random.choice(st.session_state.entradas_codigos if t=="E" else st.session_state.saidas_codigos)
            for t in tipos
        ],
        "cliente_fornecedor": [
            f"{'C' if t=='E' else 'F'}{random.randint(1,50)}" for t in tipos
        ],
        "tesouraria": [escolha(st.session_state.lista_tesouraria) for _ in range(n)],
        "centro_custo": [escolha(st.session_state.lista_cc) for _ in range(n)],
        "tipo_doc": [escolha(st.session_state.lista_tipos) for _ in range(n)]
    })
    return registros

# -------------------------------------------------
# 🔄 NAVEGAÇÃO ENTRE ETAPAS
# -------------------------------------------------
def avancar_step():
    st.session_state.step += 1

def voltar_step():
    if st.session_state.step > 0:
        st.session_state.step -= 1

def botoes_step(preenchido=True, label_proximo="Próximo ➡"):
    col1, col2 = st.columns([1, 1])
    with col1:
        st.button("⬅ Voltar", on_click=voltar_step)
    with col2:
        if preenchido:
            st.button(label_proximo, on_click=avancar_step)

# -------------------------------------------------
# 🧾 BOTÃO DE RESET GLOBAL
# -------------------------------------------------
if st.button("🔄 Resetar Tudo"):
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.rerun()

# -------------------------------------------------
# 📘 OBSERVAÇÕES
# -------------------------------------------------
with st.expander("ℹ️ Observações da função", expanded=False):
    st.info("""
        - Gera documentos fictícios de entradas e saídas financeiras.
        - Os parâmetros devem ser preenchidos/importados com os códigos cadastrados no Fluxo.
        - O período de geração define as datas de vencimento e liquidação.
    """)

# -------------------------------------------------
# 🧭 FLUXO PRINCIPAL (WIZARD)
# -------------------------------------------------
step = st.session_state.step
st.progress((step + 1) / 7)

# Passo 0 - Período
if step == 0:
    st.markdown("### 📅 Selecionar Período")
    data_inicio_str = st.text_input("Data inicial", value=st.session_state.data_inicio.strftime("%d/%m/%Y"))
    data_fim_str = st.text_input("Data final", value=st.session_state.data_fim.strftime("%d/%m/%Y"))

    def validar_data(data_str):
        try:
            return datetime.strptime(data_str, "%d/%m/%Y").date()
        except ValueError:
            return None

    data_inicio = validar_data(data_inicio_str)
    data_fim = validar_data(data_fim_str)

    if data_inicio is None:
        st.error("Data inicial inválida! Use o formato dd/mm/aaaa")
    elif data_fim is None:
        st.error("Data final inválida! Use o formato dd/mm/aaaa")
    elif data_fim < data_inicio:
        st.error("A data final não pode ser anterior à data inicial!")
    else:
        st.button(
            "Próximo: Unidades ➡",
            on_click=lambda: st.session_state.update({
                "data_inicio": data_inicio,
                "data_fim": data_fim
            }) or avancar_step()
        )

# Passo 1 - Unidades
elif step == 1:
    preenchido = atualizar_lista("Unidades", st.session_state.lista_unidades, "unidades", "unidades")
    botoes_step(preenchido, "Próximo: Classificações ➡")

# Passo 2 - Classificações
elif step == 2:
    st.markdown("<h2>Classificações financeiras</h2>", unsafe_allow_html=True)
    entradas_ok = atualizar_lista("Entradas", st.session_state.entradas_codigos, "entrada", "entradas")
    saidas_ok = atualizar_lista("Saídas", st.session_state.saidas_codigos, "saida", "saidas")
    botoes_step(entradas_ok and saidas_ok, "Próximo: Tesouraria ➡")

# Passo 3 - Tesouraria
elif step == 3:
    preenchido = atualizar_lista("Tesouraria", st.session_state.lista_tesouraria, "tesouraria", "tesouraria")
    botoes_step(preenchido, "Próximo: Centro de Custo ➡")

# Passo 4 - Centro de Custo
elif step == 4:
    preenchido = atualizar_lista("Centro de Custo", st.session_state.lista_cc, "centro_custo", "cc")
    botoes_step(preenchido, "Próximo: Tipos de Documento ➡")

# Passo 5 - Tipos de Documento
elif step == 5:
    preenchido = atualizar_lista("Tipos de Documento", st.session_state.lista_tipos, "tipos_doc", "tipos_doc")
    botoes_step(preenchido, "Próximo: Gerar CSV ➡")

# Passo 6 - Geração CSV
elif step == 6:
    st.markdown("### 💾 Gerar CSV com dados")
    num_registros = st.number_input("Número de registros", min_value=10, max_value=10000, value=100)

    if st.button("Gerar Registros"):
        df = gerar_registros_csv(num_registros)
        st.session_state.registros_gerados = df
        st.session_state.csv_gerado = True

    botoes_step(preenchido=True, label_proximo="⬅ Voltar")

    if st.session_state.csv_gerado:
        df = st.session_state.registros_gerados
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        st.download_button("📥 Download CSV", data=csv_buffer.getvalue(),
                           file_name="documentos.csv", mime="text/csv")

        st.subheader("📊 Resumo de Registros")
        entradas = df[df['natureza'] == 'E']
        saidas = df[df['natureza'] == 'S']

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Entradas", entradas.shape[0])
            st.metric("Valor total Entradas", f"R$ {entradas['valor'].sum():,.2f}")
        with col2:
            st.metric("Saídas", saidas.shape[0])
            st.metric("Valor total Saídas", f"R$ {saidas['valor'].sum():,.2f}")