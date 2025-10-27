import streamlit as st
import random
import io
import pandas as pd
from datetime import datetime, timedelta

# -----------------------------
# Configuração inicial
# -----------------------------
st.set_page_config(page_title="Gerador de documentos fictícios", layout="wide")
st.markdown("<h1 style='text-align:center; color:#5a7be0;'>Gerador de Documentos Fictícios (Fluxo)</h1>", unsafe_allow_html=True)

# -----------------------------
# Inicialização do session_state
# -----------------------------
def init_state(key, default):
    if key not in st.session_state:
        st.session_state[key] = default

init_state("step", 0)
init_state("data_inicio", datetime(2025, 1, 1))
init_state("data_fim", datetime(2025, 12, 31))
init_state("lista_unidades", ["01", "02", "03"])
init_state("entradas_codigos", ["E001", "E002"])
init_state("saidas_codigos", ["S001", "S002"])
init_state("lista_tesouraria", ["T001", "T002"])
init_state("lista_cc", ["CC01", "CC02"])
init_state("lista_tipos", ["NF", "REC"])
init_state("registros_gerados", [])

# -----------------------------
# CSS global para botão amarelo claro
# -----------------------------
st.markdown("""
<style>
div.stButton > button {
    background-color: #fff59d !important;  /* amarelo claro */
    color: black !important;
    font-weight: bold;
    border-radius: 8px;
    padding: 0.5em 1em;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Funções auxiliares
# -----------------------------
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

def atualizar_lista(nome, lista_padrao, tipo_arquivo, key):
    st.write(f"### {nome}")
    col1, col2 = st.columns([1,1])
    lista = lista_padrao.copy()
    with col1:
        st.download_button(f"📥 Modelo {nome}", data=gerar_template_xlsx(tipo_arquivo), file_name=f"{nome}_template.xlsx", key=f"dl_{nome}")
    with col2:
        arquivo = st.file_uploader(f"Importar {nome}", type=["xlsx"], key=f"upload_{key}")
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
    entrada = st.text_area(f"{nome} (separados por vírgula)", value=",".join(lista))
    lista = [x.strip() for x in entrada.split(",") if x.strip()]
    st.session_state[f"lista_{key}"] = lista
    return len(lista) > 0

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

def exibir_dashboard(df):
    st.subheader("📊 Mini-Dashboard")
    col1, col2 = st.columns(2)
    with col1:
        entradas = df[df['tipo']=='E'].shape[0]
        saídas = df[df['tipo']=='S'].shape[0]
        st.metric("Entradas", entradas)
        st.metric("Saídas", saídas)
    with col2:
        total_valor = df['valor'].sum()
        st.metric("Valor total", f"R$ {total_valor:,.2f}")

# -----------------------------
# Função para avançar passo
# -----------------------------
def avancar_step():
    st.session_state.step += 1

# -----------------------------
# Expander de Observações
# -----------------------------
with st.expander("Observações da função", expanded=False):
    st.info("""
        - Gera documentos fictícios de entradas e saídas financeiras.
        - Os parâmetros devem ser preenchidos/importados com os códigos cadastrados no Fluxo.
        - O período de geração é determinado pelas datas inicial e final.
        - Datas identificam vencimento; liquidação pode ser aleatória.
    """)

# -----------------------------
# Wizard passo a passo
# -----------------------------
step = st.session_state.step

# -----------------------------
# Passo 0 - Período
# -----------------------------
if step == 0:
    st.markdown("### 📅 Selecionar Período")
    
    # Valores iniciais no formato dd/mm/aaaa
    data_inicio_str = st.text_input(
        "Data inicial", value=st.session_state.data_inicio.strftime("%d/%m/%Y")
    )
    data_fim_str = st.text_input(
        "Data final", value=st.session_state.data_fim.strftime("%d/%m/%Y")
    )

    # Função para validar a data no formato dd/mm/aaaa
    def validar_data(data_str):
        try:
            return datetime.strptime(data_str, "%d/%m/%Y").date()
        except ValueError:
            return None

    data_inicio = validar_data(data_inicio_str)
    data_fim = validar_data(data_fim_str)

    # Validações e mensagens de erro
    if data_inicio is None:
        st.error("Data inicial inválida! Use o formato dd/mm/aaaa")
    elif data_fim is None:
        st.error("Data final inválida! Use o formato dd/mm/aaaa")
    elif data_fim < data_inicio:
        st.error("A data final não pode ser menor que a inicial!")
    else:
        st.button(
            "Próximo: Unidades",
            on_click=lambda: st.session_state.update({
                "data_inicio": data_inicio,
                "data_fim": data_fim
            }) or avancar_step()
        )


# Passo 1 - Unidades
elif step == 1:
    preenchido = atualizar_lista("Unidades", st.session_state.lista_unidades, "unidades", "unidades")
    if preenchido:
        st.button("Próximo: Classificações", on_click=avancar_step)

# Passo 2 - Classificações
elif step == 2:
    entradas_ok = atualizar_lista("Entradas", st.session_state.entradas_codigos, "entrada", "entradas")
    saidas_ok = atualizar_lista("Saídas", st.session_state.saidas_codigos, "saida", "saidas")
    if entradas_ok and saidas_ok:
        st.button("Próximo: Tesouraria", on_click=avancar_step)

# Passo 3 - Tesouraria
elif step == 3:
    preenchido = atualizar_lista("Tesouraria", st.session_state.lista_tesouraria, "tesouraria", "tesouraria")
    if preenchido:
        st.button("Próximo: Centro de Custo", on_click=avancar_step)

# Passo 4 - Centro de Custo
elif step == 4:
    preenchido = atualizar_lista("Centro de Custo", st.session_state.lista_cc, "centro_custo", "cc")
    if preenchido:
        st.button("Próximo: Tipos de Documento", on_click=avancar_step)

# Passo 5 - Tipos de Documento
elif step == 5:
    preenchido = atualizar_lista("Tipos de Documento", st.session_state.lista_tipos, "tipos_doc", "tipos_doc")
    if preenchido:
        st.button("Próximo: Gerar CSV", on_click=avancar_step)

# -----------------------------
# Passo 6 - Gerar CSV
# -----------------------------
elif step == 6:
    st.markdown("### 💾 Gerar CSV com dados")
    
    num_registros = st.number_input(
        "Número de registros", min_value=10, max_value=10000, value=100
    )

    # Função que gera registros com datas já no formato dd/mm/aaaa
    def gerar_registros_csv(n):
        registros = []
        for id_counter in range(1, n+1):
            tipo = random.choice(["E", "S"])
            descricao = random.choice(st.session_state.entradas_codigos if tipo=="E" else st.session_state.saidas_codigos)
            valor = round(random.uniform(1, 101000), 2)
            
            # Datas aleatórias dentro do período
            vencimento = st.session_state.data_inicio + timedelta(days=random.randint(0, (st.session_state.data_fim - st.session_state.data_inicio).days))
            pagamento = vencimento + timedelta(days=random.randint(-5,5)) if random.random() < 0.5 else None
            
            # Converte para string dd/mm/aaaa
            venc_str = vencimento.strftime("%d/%m/%Y")
            pagamento_str = pagamento.strftime("%d/%m/%Y") if pagamento else ""
            
            cliente_fornecedor = f"C{random.randint(1,50)}" if tipo=="E" else f"F{random.randint(1,50)}"
            
            registros.append([
                id_counter, tipo, valor, random.choice(st.session_state.lista_unidades),
                venc_str, pagamento_str, descricao, cliente_fornecedor,
                random.choice(st.session_state.lista_tesouraria) if st.session_state.lista_tesouraria else "",
                random.choice(st.session_state.lista_cc) if st.session_state.lista_cc else "",
                random.choice(st.session_state.lista_tipos) if st.session_state.lista_tipos else ""
            ])
        return registros

    # Função que gera CSV e atualiza session_state
    def gerar_csv():
        registros = gerar_registros_csv(num_registros)
        df = pd.DataFrame(registros, columns=[
            "documento","tipo","valor","cod_unidade","data_venc","data_liq",
            "descricao","cliente_fornecedor","tesouraria","centro_custo","tipo_documento"
        ])
        st.session_state.registros_gerados = df
        st.session_state.csv_gerado = True

    # Botão amarelo claro para gerar CSV
    st.button("Gerar CSV", on_click=gerar_csv)

    # Após gerar CSV, exibe download e dashboards
    if st.session_state.get("csv_gerado", False):
        df = st.session_state.registros_gerados

        # Download CSV
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        st.download_button(
            "📥 Download CSV", 
            data=csv_buffer.getvalue(), 
            file_name="documentos.csv", 
            mime="text/csv"
        )

        # Dashboard com quantidade e valor separados por Entradas e Saídas
        st.subheader("📊 Registros e Valores")
        entradas_valor = df[df['tipo']=='E']['valor'].sum()
        saidas_valor = df[df['tipo']=='S']['valor'].sum()
        entradas_qtd = df[df['tipo']=='E'].shape[0]
        saidas_qtd = df[df['tipo']=='S'].shape[0]

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Quantidade de Entradas", entradas_qtd)
            st.metric("Valor total Entradas", f"R$ {entradas_valor:,.2f}")
        with col2:
            st.metric("Quantidade de Saídas", saidas_qtd)
            st.metric("Valor total Saídas", f"R$ {saidas_valor:,.2f}")