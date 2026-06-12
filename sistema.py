import streamlit as st

st.set_page_config(page_title="Controle de Manutenção & PT", layout="wide", page_icon="⚙️")

# --- BANCO DE DADOS TEMPORÁRIO ---
if "equipamentos" not in st.session_state:
    st.session_state.equipamentos = [
        {"id": "EQ-001", "nome": "Torno Mecânico Nardini", "localizacao": "Oficina Central", "criticidade": "Alta"},
        {"id": "EQ-002", "nome": "Compressor de Ar Schulz", "localizacao": "Sala de Compressores", "criticidade": "Média"},
    ]

if "historico" not in st.session_state:
    st.session_state.historico = [
        {"data": "12/06/2026", "equipamento": "Torno Mecânico Nardini", "tipo": "Corretiva", "descricao": "Troca de correia dentada", "executor": "Carlos Silva"}
    ]

if "planejamento" not in st.session_state:
    st.session_state.planejamento = [
        {"id": 1, "equipamento": "Torno Mecânico Nardini", "periodo": "Semanal", "pecas": "Filtro de óleo", "status": "Pendente", "seguranca": "Uso obrigatório de óculos de proteção. Desenergizar o equipamento (Lockout/Tagout)."},
        {"id": 2, "equipamento": "Compressor de Ar Schulz", "periodo": "Mensal", "pecas": "Óleo lubrificante", "status": "Pendente", "seguranca": "Aliviar pressão interna do sistema antes de iniciar. Bloquear chave geral elétrica."}
    ]

st.sidebar.title("⚙️ Gestão de Manutenção")
menu = st.sidebar.radio("Navegar para:", ["Catálogo de Equipamentos", "Planejamento (Semanal/Mensal/Anual)", "Histórico de Serviços", "Emissão de Permissão de Trabalho (PT)"])

# 1. CATÁLOGO
if menu == "Catálogo de Equipamentos":
    st.header("📋 Catálogo de Máquinas e Equipamentos")
    with st.expander("➕ Cadastrar Novo Equipamento"):
        with st.form("form_equipamento"):
            id_eq = st.text_input("Código/Tag do Equipamento:")
            nome_eq = st.text_input("Nome do Equipamento:")
            local_eq = st.text_input("Localização / Setor:")
            crit_eq = st.selectbox("Criticidade:", ["Baixa", "Média", "Alta"])
            if st.form_submit_button("Salvar Equipamento"):
                if id_eq and nome_eq:
                    st.session_state.equipamentos.append({"id": id_eq, "nome": nome_eq, "localizacao": local_eq, "criticidade": crit_eq})
                    st.success("Equipamento cadastrado com sucesso!")
                    st.rerun()
    st.table(st.session_state.equipamentos)

# 2. PLANEJAMENTO
elif menu == "Planejamento (Semanal/Mensal/Anual)":
    st.header("📅 Planejamento de Manutenções Preventivas")
    aba_sem, aba_mes, aba_ano, aba_novo = st.tabs(["🗓️ Semanal", "📅 Mensal", "⏳ Anual", "➕ Agendar Preventiva"])
    
    def exibir_tabela(frequencia):
        dados = [p for p in st.session_state.planejamento if p['periodo'] == frequencia]
        if dados: st.table(dados)
        else: st.info(f"Nenhuma manutenção para o período {frequencia}.")

    with aba_sem: exibir_tabela("Semanal")
    with aba_mes: exibir_tabela("Mensal")
    with aba_ano: exibir_tabela("Anual")
    with aba_novo:
        with st.form("form_plan"):
            eq_escolhido = st.selectbox("Equipamento:", [e['nome'] for e in st.session_state.equipamentos])
            periodo_escolhido = st.selectbox("Período:", ["Semanal", "Mensal", "Anual"])
            pecas_necessarias = st.text_area("Peças a serem Trocadas:")
            regras_seguranca = st.text_area("Instruções de Segurança:")
            if st.form_submit_button("Salvar"):
                st.session_state.planejamento.append({
                    "id": len(st.session_state.planejamento) + 1, "equipamento": eq_escolhido,
                    "periodo": periodo_escolhido, "pecas": pecas_necessarias, "status": "Pendente", "seguranca": regras_seguranca
                })
                st.success("Agendado!")
                st.rerun()

# 3. HISTÓRICO
elif menu == "Histórico de Serviços":
    st.header("📜 Histórico de Manutenções Realizadas")
    st.table(st.session_state.historico)

# 4. PERMISSÃO DE TRABALHO
elif menu == "Emissão de Permissão de Trabalho (PT)":
    st.header("⚠️ Emissão de Permissão de Trabalho (PT)")
    opcoes_pt = {f"{p['id']} - {p['equipamento']}": p for p in st.session_state.planejamento if p['status'] == "Pendente"}
    
    if opcoes_pt:
        selecao = st.selectbox("Selecione a Manutenção:", list(opcoes_pt.keys()))
        manutencao_selecionada = opcoes_pt[selecao]
        colaborador = st.text_input("Nome do Colaborador Executante:")
        
        if st.button("Gerar Permissão de Trabalho Oficial"):
            if colaborador:
                st.markdown(f"""
                <div style="border: 2px solid #FF4B4B; padding: 20px; border-radius: 10px; background-color: #FFF5F5; color: black;">
                    <h2 style="text-align: center; color: #FF4B4B;">⚠️ PERMISSÃO DE TRABALHO (PT)</h2>
                    <p><strong>Colaborador Autorizado:</strong> {colaborador}</p>
                    <p><strong>Equipamento:</strong> {manutencao_selecionada['equipamento']}</p>
                    <p><strong>Peças para Troca:</strong> {manutencao_selecionada['pecas']}</p>
                    <h4 style="color: #FF4B4B;">🛑 DESCRITIVO DE SEGURANÇA:</h4>
                    <p style="background-color: #FFE6E6; padding: 10px; border-left: 5px solid #FF4B4B;">{manutencao_selecionada['seguranca']}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error("Digite o nome do colaborador.")
    else:
        st.info("Nenhuma manutenção pendente.")
