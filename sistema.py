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

# 1. CATÁLOGO (Usa blocos divs estilizados em vez de st.table)
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
    
    # Renderização em formato de cards visuais para abolir o uso do numpy
    for eq in st.session_state.equipamentos:
        cor_critica = "#FF4B4B" if eq['criticidade'] == "Alta" else "#FFAA00" if eq['criticidade'] == "Média" else "#00CC66"
        st.markdown(f"""
        <div style="padding:15px; border-radius:8px; background-color:#F0F2F6; margin-bottom:10px; border-left: 6px solid {cor_critica}; color: black;">
            <span style="font-size:12px; font-weight:bold; color:#555;">TAG: {eq['id']}</span>
            <h4 style="margin:2px 0; color:#111;">{eq['nome']}</h4>
            <p style="margin:0; font-size:14px;">📍 <b>Setor:</b> {eq['localizacao']} | 🔥 <b>Criticidade:</b> <span style="color:{cor_critica}; font-weight:bold;">{eq['criticidade']}</span></p>
        </div>
        """, unsafe_allow_html=True)

# 2. PLANEJAMENTO
elif menu == "Planejamento (Semanal/Mensal/Anual)":
    st.header("📅 Planejamento de Manutenções Preventivas")
    aba_sem, aba_mes, aba_ano, aba_novo = st.tabs(["🗓️ Semanal", "📅 Mensal", "⏳ Anual", "➕ Agendar Preventiva"])
    
    def exibir_blocos(frequencia):
        dados = [p for p in st.session_state.planejamento if p['periodo'] == frequencia]
        if dados:
            for p in dados:
                st.markdown(f"""
                <div style="padding:15px; border-radius:8px; background-color:#EBF5FF; margin-bottom:10px; border-left: 6px solid #0066CC; color: black;">
                    <h5 style="margin:0; color:#0066CC;">⚙️ {p['equipamento']}</h5>
                    <p style="margin:4px 0 0 0; font-size:14px;">🔧 <b>Peças para Troca:</b> {p['pecas']}</p>
                    <p style="margin:2px 0 0 0; font-size:14px;">🛡️ <b>Segurança:</b> {p['seguranca']}</p>
                    <p style="margin:2px 0 0 0; font-size:12px; color:#555;">📌 Status: <b>{p['status']}</b></p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info(f"Nenhuma manutenção cadastrada para o período {frequencia}.")

    with aba_sem: exibir_blocos("Semanal")
    with aba_mes: exibir_blocos("Mensal")
    with aba_ano: exibir_blocos("Anual")
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
    for h in st.session_state.historico:
        st.markdown(f"""
        <div style="padding:15px; border-radius:8px; background-color:#EAF9EE; margin-bottom:10px; border-left: 6px solid #28A745; color: black;">
            <span style="font-size:12px; color:#555;">📅 Data de Conclusão: {h['data']}</span>
            <h5 style="margin:2px 0; color:#155724;">✅ {h['equipamento']}</h5>
            <p style="margin:0; font-size:14px;">📝 <b>Serviço:</b> {h['descricao']} | <b>Executor:</b> {h['executor']}</p>
        </div>
        """, unsafe_allow_html=True)

# 4. PERMISSÃO DE TRABALHO
elif menu == "Emissão de Permissão de Trabalho (PT)":
    st.header("⚠️ Emissão de Permissão de Trabalho (PT)")
    opcoes_pt = {f"{p['id']} - {p['equipamento']}": p for p in st.session_state.planejamento if p['status'] == "Pendente"}
    
    if opcoes_pt:
        selecao = st.selectbox("Selecione a Manutenção:", list(opcoes_pt.keys()))
        manutencao_selecionada = opcoes_pt[selecao]
        colaborador = st.text_input("Nome do Colaborador Executante (Nominal):")
        
        if st.button("Gerar Permissão de Trabalho Oficial"):
            if colaborador:
                st.markdown(f"""
                <div style="border: 2px solid #FF4B4B; padding: 20px; border-radius: 10px; background-color: #FFF5F5; color: black;">
                    <h2 style="text-align: center; color: #FF4B4B; margin-top:0;">⚠️ PERMISSÃO DE TRABALHO (PT) - Nº 00{manutencao_safe := manutencao_selecionada['id']}</h2>
                    <hr style="border: 1px solid #FF4B4B;">
                    <p><strong>Colaborador Autorizado:</strong> {colaborador}</p>
                    <p><strong>Equipamento Alvo:</strong> {manutencao_selecionada['equipamento']}</p>
                    <p><strong>Peças para Substituição:</strong> {manutencao_selecionada['pecas']}</p>
                    <hr style="border: 0.5px dashed #FF4B4B;">
                    <h4 style="color: #FF4B4B; margin-bottom: 5px;">🛑 DESCRITIVO DE SEGURANÇA OBRIGATÓRIO:</h4>
                    <p style="background-color: #FFE6E6; padding: 10px; border-left: 5px solid #FF4B4B;">{manutencao_selecionada['seguranca']}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error("Digite o nome do colaborador.")
    else:
        st.info("Nenhuma manutenção pendente para emissão de PT.")
