# -----------------------------
# Funções para avançar e voltar passo
# -----------------------------
def avancar_step():
    st.session_state.step += 1

def voltar_step():
    if st.session_state.step > 0:
        st.session_state.step -= 1

# -----------------------------
# Função auxiliar para criar botões estilizados
# -----------------------------
def botoes_step(preenchido=True, label_proximo="Próximo ➡"):
    col1, col2 = st.columns([1,1])

    # Botão Voltar (laranja)
    with col1:
        if st.button("⬅ Voltar", on_click=voltar_step):
            pass  # on_click já atualiza session_state

    # Botão Avançar (amarelo)
    with col2:
        if preenchido:
            if st.button(label_proximo, on_click=avancar_step):
                pass  # on_click já atualiza session_state

# -----------------------------
# Wizard passo a passo
# -----------------------------
step = st.session_state.step

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
        col1, col2 = st.columns([1,1])
        with col2:
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

# Passo 6 - Gerar CSV
elif step == 6:
    st.markdown("### 💾 Gerar CSV com dados")
    num_registros = st.number_input("Número de registros", min_value=10, max_value=10000, value=100)

    def gerar_csv():
        registros = gerar_registros_csv(num_registros)
        df = pd.DataFrame(registros, columns=[
            "documento","natureza","valor","unidade","data_venc","data_liq",
            "descricao","cliente_fornecedor","tesouraria","centro_custo","tipo_documento"
        ])
        st.session_state.registros_gerados = df
        st.session_state.csv_gerado = True

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