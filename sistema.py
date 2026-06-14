import streamlit as st
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Controle de Manutenção & PT", layout="wide", page_icon="⚙️")

# --- BANCO DE DADOS EM MEMÓRIA ATIVA (BLINDADO CONTRA TRAVAMENTOS DE ARQUIVO) ---
if "equipamentos" not in st.session_state:
    st.session_state.equipamentos = [
        {
            "id": "EQ-001", 
            "nome": "Torno Mecânico Nardini", 
            "localizacao": "Oficina Central", 
            "criticidade": "Alta",
            "check_semanal": "Verificar nível de óleo e lubrificação geral\nLimpeza de resíduos e cavacos\nTestar botão de emergência",
            "check_mensal": "Trocar filtros de óleo\nVerificar tensão de correias",
            "check_anual": "Revisão do motor elétrico\nSubstituição do fluido hidráulico"
        },
        {
            "id": "EQ-002", 
            "nome": "Compressor de Ar Schulz", 
            "localizacao": "Sala de Compressores", 
            "criticidade": "Média",
            "check_semanal": "Drenar condensado do reservatório\nVerificar ruídos anormais",
            "check_mensal": "Limpar filtro de ar\nVerificar nível de óleo",
            "check_anual": "Teste hidrostático do vaso\nTroca de válvulas de segurança"
        }
    ]

if "planejamento" not in st.session_state:
    st.session_state.planejamento = []

if "historico" not in st.session_state:
    st.session_state.historico = []

# --- INJEÇÃO DA MARCA NO CANTO INFERIOR DIREITO DA TELA (TAMANHO ÍCONE ESTÁTICO) ---
st.markdown(
    """
    <div style="position: fixed; bottom: 12px; right: 12px; z-index: 9999; display: flex; align-items: center; justify-content: center; background-color: #262730; border: 1px solid #FF4B4B; width: 32px; height: 32px; border-radius: 6px; box-shadow: 0 2px 4px rgba(0,0,0,0.3); pointer-events: none;">
        <span style="font-size: 8px; font-family: sans-serif; font-weight: bold; color: #FF4B4B; letter-spacing: 0.2px;">GDCOM</span>
    </div>
    """,
    unsafe_allow_html=True
)

# --- MENU LATERAL DE NAVEGAÇÃO ORIGINAL ---
st.sidebar.title("⚙️ Gestão de Manutenção")
menu = st.sidebar.radio("Navegar para:", [
    "📋 Cadastro & Edição de Máquinas", 
    "📅 Planejamento & Checklists", 
    "📜 Histórico de Trocas", 
    "⚠️ Emissão de PT"
])

st.sidebar.markdown("---")
st.sidebar.caption("Controle Operacional Industrial")

# ==========================================
# 1. CADASTRO, EDIÇÃO E EXCLUSÃO
# ==========================================
if menu == "📋 Cadastro & Edição de Máquinas":
    st.header("📋 Gerenciamento de Máquinas e Equipamentos")
    aba_lista, aba_cadastrar, aba_editar = st.tabs(["🔍 Ver e Excluir", "➕ Cadastrar Novo", "✏️ Editar Existente"])
    
    with aba_lista:
        st.subheader("Equipamentos Registrados no Sistema")
        if not st.session_state.equipamentos:
            st.info("Nenhum equipamento cadastrado.")
        for eq in st.session_state.equipamentos:
            st.write(f"🔹 **[{eq['id']}] {eq['nome']}** | Setor: {eq['localizacao']} | Criticidade: {eq['criticidade']}")
            if st.button(f"🗑️ Remover {eq['id']}", key=f"del_{eq['id']}"):
                st.session_state.equipamentos = [e for e in st.session_state.equipamentos if e['id'] != eq['id']]
                st.success(f"Equipamento {eq['id']} removido com sucesso!")
                st.rerun()
            st.write("---")
                        
    with aba_cadastrar:
        st.subheader("Cadastrar Nova Máquina")
        with st.form("form_cadastro"):
            id_eq = st.text_input("Código/Tag do Equipamento (Ex: EQ-003):")
            nome_eq = st.text_input("Nome do Equipamento:")
            local_eq = st.text_input("Localização / Setor:")
            crit_eq = st.selectbox("Criticidade:", ["Baixa", "Média", "Alta"])
            st.markdown("---")
            st.subheader("📋 Definição dos Itens Fixos de Preventiva (Coloque um por linha):")
            c_sem = st.text_area("Itens da Preventiva Semanal:", "Verificar nível de óleo\nLimpeza geral")
            c_mes = st.text_area("Itens da Preventiva Mensal:", "Trocar filtros\nConferir correias")
            c_ano = st.text_area("Itens da Preventiva Anual:", "Revisão geral do motor")
            
            if st.form_submit_button("Salvar Equipamento"):
                if id_eq and nome_eq:
                    if any(e['id'] == id_eq for e in st.session_state.equipamentos):
                        st.error("Tag duplicada.")
                    else:
                        st.session_state.equipamentos.append({
                            "id": id_eq, "nome": nome_eq, "localizacao": local_eq, "criticidade": crit_eq,
                            "check_semanal": c_sem, "check_mensal": c_mes, "check_anual": c_ano
                        })
                        st.success("Máquina registrada com sucesso!")
                        st.rerun()
                else:
                    st.error("Preencha os campos obrigatórios.")

    with aba_editar:
        st.subheader("Editar Máquina Existente")
        if not st.session_state.equipamentos:
            st.info("Nenhum equipamento disponível para edição.")
        else:
            opcoes_edicao = {f"{e['id']} - {e['nome']}": e for e in st.session_state.equipamentos}
            selecionado_edicao = st.selectbox("Selecione qual máquina deseja alterar:", list(opcoes_edicao.keys()))
            eq_para_editar = opcoes_edicao[selecionado_edicao]
            
            with st.form("form_edicao"):
                novo_nome = st.text_input("Nome do Equipamento:", value=eq_para_editar['nome'])
                novo_local = st.text_input("Localização / Setor:", value=eq_para_editar['localizacao'])
                novo_crit = st.selectbox("Criticidade:", ["Baixa", "Média", "Alta"], index=["Baixa", "Média", "Alta"].index(eq_para_editar['criticidade']))
                st.markdown("---")
                st.subheader("✏️ Editar Itens de Verificação da Máquina:")
                n_sem = st.text_area("Preventiva Semanal:", value=eq_para_editar.get('check_semanal', ''))
                n_mes = st.text_area("Preventiva Mensal:", value=eq_para_editar.get('check_mensal', ''))
                n_ano = st.text_area("Preventiva Anual:", value=eq_para_editar.get('check_anual', ''))
                
                if st.form_submit_button("Gravar Alterações"):
                    for e in st.session_state.equipamentos:
                        if e['id'] == eq_para_editar['id']:
                            e['nome'] = novo_nome
                            e['localizacao'] = novo_local
                            e['criticidade'] = novo_crit
                            e['check_semanal'] = n_sem
                            e['check_mensal'] = n_mes
                            e['check_anual'] = n_ano
                    st.success("Alterações salvas com sucesso!")
                    st.rerun()

# ==========================================
# 2. PLANEJAMENTO TEMPORAL (CORRIGIDO E SEPARADO)
# ==========================================
elif menu == "📅 Planejamento & Checklists":
    st.header("📅 Planejamento de Manutenções Preventivas")
    aba_sem, aba_mes, aba_ano, aba_novo = st.tabs(["🗓️ Semanal", "📅 Mensal", "⏳ Anual", "➕ Agendar Preventiva"])
    
    def exibir_itens(frequencia, chave_check):
        dados = [p for p in st.session_state.planejamento if p['periodo'] == frequencia and p['status'] == "Pendente"]
        if dados:
            for p in dados:
                st.write(f"⚙️ **{p['equipamento']}** | 📅 **Data Prevista:** {p.get('data_prevista')} | **Status:** {p['status']}")
                st.write(f"🔧 Peças Programadas para Troca: {p['pecas']}")
                maq = next((e for e in st.session_state.equipamentos if e['nome'] == p['equipamento']), None)
                if maq and maq.get(chave_check):
                    st.caption("📋 **Itens Específicos que serão verificados nesta máquina:**")
                    for item in maq[chave_check].split('\n'):
                        if item.strip():
                            st.caption(f" ▢ {item.strip()}")
                st.write("---")
        else:
            st.info(f"Nenhuma manutenção pendente para {frequencia}.")

    with aba_sem: exibir_itens("Semanal", "check_semanal")
    with aba_mes: exibir_itens("Mensal", "check_mensal")
    with aba_ano: exibir_itens("Anual", "check_anual")
    
    with aba_novo:
        st.subheader("📋 Agendar Nova Ordem de Preventiva")
        lista_nomes = [e['nome'] for e in st.session_state.equipamentos]
        
        if not lista_nomes:
            st.warning("Cadastre uma máquina primeiro na aba de Cadastro.")
        else:
            eq_escolhido = st.selectbox("1. Selecione a Máquina Alvo:", lista_nomes, key="plan_eq")
            periodo_escolhido = st.selectbox("2. Escolha o Período / Frequência:", ["Semanal", "Mensal", "Anual"], key="plan_per")
            data_planejada = st.date_input("3. Selecione a Data para Executar o Serviço:", datetime.now(), key="plan_data")
            pecas_necessarias = st.text_area("4. Descrição das Peças a serem Trocadas:", key="plan_pecas")
            regras_seguranca = st.text_area("5. Instruções de Segurança Específicas:", value="Uso obrigatório de EPIs adequados. Desenergizar o equipamento (Lockout/Tagout).", key="plan_seg")
            
            if st.button("💾 Gravar e Agendar Manutenção Definitivamente", key="btn_gravar_preventiva"):
                st.session_state.planejamento.append({
                    "id": len(st.session_state.planejamento) + 1, 
                    "equipamento": eq_escolhido,
                    "periodo": periodo_escolhido, 
                    "data_prevista": data_planejada.strftime('%d/%m/%Y'),
                    "pecas": pecas_necessarias, 
                    "status": "Pendente", 
                    "seguranca": regras_seguranca
                })
