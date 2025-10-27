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
# CSS para botões
# -----------------------------

st.markdown("""
<style>
#botao_voltar button {
    background-color: #ffc59d;
    color: black !important;
    font-weight: bold;
    border-radius: 8px;
    padding: 0.5em 1em;
}
#botao_avancar button {
    background-color: #fff59d !important;
    color: black !important;
    font-weight: bold;
    border-radius: 8px;
    padding: 0.5em 1em;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# CSS para cards das etapas
# -----------------------------
st.markdown("""
<style>
.card-step {
    background-color: #f9f9f9;
    border-radius: 12px;
    padding: 15px;
    margin-bottom: 15px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.1);
}
.card-step h3 {
    margin-top: 0;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# CSS para card de classificações
# -----------------------------
st.markdown("""
<style>
.card-step {
    background-color: #f9f9f9;
    border-radius: 12px;
    padding: 15px;
    margin-bottom: 15px;
    box-shadow: 0 1px 6px rgba(0,0,0,0.1);
}
.card-step h2 {
    margin-top: 0;
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

def atualizar_lista_card(nome, lista_padrao, tipo_arquivo, key):
    lista = lista_padrao.copy()
    
    with st.container():
        st.markdown(f"<div class='card-step'><h3>{nome}</h3></div>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([1,1])
        with col1:
            st.download_button(
                f"📥 Modelo {nome}", 
                data=gerar_template_xlsx(tipo_arquivo), 
                file_name=f"{nome}_template.xlsx", 
                key=f"dl_{nome}"
            )
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

        lista_str = ",".join(lista)
        lista_text = st.text_area(f"{nome} (separados por vírgula)", value=lista_str, height=60)
        lista = [x.strip() for x in lista_text.split(",") if x.strip()]
        st.session_state[f"lista_{key}"] = lista
    
    return len(lista) > 0

def gerar_registros_csv(n):
    registros = []
    hoje = datetime.today()
    data_inicio = st.session_state.data_inicio
    data_fim = st.session_state.data_fim

    for id_counter in range(1, n+1):
        tipo = random.choice(["E", "S"])
        descricao = random.choice(
            st.session_state.entradas_codigos if tipo=="E" else st.session_state.saidas_codigos
        ) if (st.session_state.entradas_codigos if tipo=="E" else st.session_state.saidas_codigos) else ""
        valor = round(random.uniform(1, 101000), 2)

        # Datas aleatórias
        vencimento = data_inicio + timedelta(days=random.randint(0, (data_fim - data_inicio).days))
        pagamento = vencimento + timedelta(days=random.randint(-5,5)) if random.random() < 0.5 else None

        # Ajusta pagamento para não passar do início ou hoje
        if pagamento:
            if pagamento < data_inicio:
                pagamento = data_inicio
            elif pagamento > hoje:
                pagamento = hoje

        venc_str = vencimento.strftime("%d/%m/%Y")
        pagamento_str = pagamento.strftime("%d/%m/%Y") if pagamento else ""
        cliente_fornecedor = f"C{random.randint(1,50)}" if tipo=="E" else f"F{random.randint(1,50)}"

        registros.append([
            id_counter,
            tipo,
            valor,
            random.choice(st.session_state.lista_unidades) if st.session_state.lista_unidades else "",
            venc_str,
            pagamento_str,
            descricao,
            cliente_fornecedor,
            random.choice(st.session_state.lista_tesouraria) if st.session_state.lista_tesouraria else "",
            random.choice(st.session_state.lista_cc) if st.session_state.lista_cc else "",
            random.choice(st.session_state.lista_tipos) if st.session_state.lista_tipos else ""
        ])
    return registros

def exibir_dashboard(df):
    st.subheader("📊 Mini-Dashboard")
    col1, col2 = st.columns(2)
    with col1:
        entradas = df[df['natureza']=='E'].shape[0]
        saidas = df[df['natureza']=='S'].shape[0]
        st.metric("Entradas", entradas)
        st.metric("Saídas", saidas)
    with col2:
        total_valor = df['valor'].sum()
        st.metric("Valor total", f"R$ {total_valor:,.2f}")

# -----------------------------
# Função para avançar passo
# -----------------------------
def avancar_step():
    st.session_state.step += 1

# -----------------------------
# Observações
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
# Funções para avançar e voltar passo
# -----------------------------
def avancar_step():
    st.session_state.step += 1

def voltar_step():
    if st.session_state.step > 0:
        st.session_state.step -= 1

# -----------------------------
# Função auxiliar para criar botões alinhados
# -----------------------------
def botoes_step(preenchido=True, label_proximo="Próximo ➡"):
    col1, col2 = st.columns([1,1])
    with col1:
        st.button("⬅ Voltar", on_click=voltar_step, key="botao_voltar")
    with col2:
        if preenchido:
            st.button(label_proximo, on_click=avancar_step, key="botao_avancar")

# -----------------------------
# Wizard passo a passo com layout consistente
# -----------------------------
step = st.session_state.step

if step == 0:
    st.markdown("<div class='card-step'><h3>📅 Selecionar Período</h3></div>", unsafe_allow_html=True)
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
        col1, col2 = st.columns([1,1])
        with col2:
            st.button(
                "Próximo: Unidades ➡",
                on_click=lambda: st.session_state.update({
                    "data_inicio": data_inicio,
                    "data_fim": data_fim
                }) or avancar_step()
            )

elif step == 1:
    preenchido = atualizar_lista_card("Unidades", st.session_state.lista_unidades, "unidades", "unidades")
    botoes_step(preenchido, "Próximo: Classificações ➡")

elif step == 2:
    st.markdown("<div class='card-step'><h2>Classificações Financeiras</h2></div>", unsafe_allow_html=True)
    entradas_ok = atualizar_lista_card("Entradas", st.session_state.entradas_codigos, "entrada", "entradas")
    saidas_ok = atualizar_lista_card("Saídas", st.session_state.saidas_codigos, "saida", "saidas")
    botoes_step(entradas_ok and saidas_ok, "Próximo: Tesouraria ➡")

elif step == 3:
    preenchido = atualizar_lista_card("Tesouraria", st.session_state.lista_tesouraria, "tesouraria", "tesouraria")
    botoes_step(preenchido, "Próximo: Centro de Custo ➡")

elif step == 4:
    preenchido = atualizar_lista_card("Centro de Custo", st.session_state.lista_cc, "centro_custo", "cc")
    botoes_step(preenchido, "Próximo: Tipos de Documento ➡")

elif step == 5:
    preenchido = atualizar_lista_card("Tipos de Documento", st.session_state.lista_tipos, "tipos_doc", "tipos_doc")
    botoes_step(preenchido, "Próximo: Gerar CSV ➡")

elif step == 6:
    st.markdown("<div class='card-step'><h3>💾 Gerar CSV com dados</h3></div>", unsafe_allow_html=True)
    num_registros = st.number_input("Número de registros", min_value=10, max_value=10000, value=100)
    botoes_step(preenchido=True, label_proximo="Gerar CSV")

    if st.session_state.get("csv_gerado", False):
        df = st.session_state.registros_gerados
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        st.download_button("📥 Download CSV", data=csv_buffer.getvalue(), file_name="documentos.csv", mime="text/csv")

        st.subheader("📊 Registros e Valores")
        entradas_valor = df[df['natureza']=='E']['valor'].sum()
        saidas_valor = df[df['natureza']=='S']['valor'].sum()
        entradas_qtd = df[df['natureza']=='E'].shape[0]
        saidas_qtd = df[df['natureza']=='S'].shape[0]

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Quantidade de Entradas", entradas_qtd)
            st.metric("Valor total Entradas", f"R$ {entradas_valor:,.2f}")
        with col2:
            st.metric("Quantidade de Saídas", saidas_qtd)
            st.metric("Valor total Saídas", f"R$ {saidas_valor:,.2f}")