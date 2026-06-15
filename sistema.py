import streamlit as st
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Controle de Manutenção & PT", layout="wide", page_icon="⚙️")

# --- BANCO DE DADOS EM MEMÓRIA ATIVA (BLINDADO) ---
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

if "pt_ativa" not in st.session_state:
    st.session_state.pt_ativa = None

# --- INDICADOR DA MARCA NO MENU LATERAL ---
st.sidebar.markdown("**Desenvolvido por GDCOM**")

# --- MENU LATERAL DE NAVEGAÇÃO ---
st.sidebar.title("⚙️ Gestão de Manutenção")
menu = st.sidebar.radio("Navegar para:", [
    "📋 Cadastro & Edição de Máquinas", 
    "📅 Planejamento & Checklists", 
    "📜 Histórico de Trocas", 
    "⚠️ Emissão de PT"
])

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
        else:
            for eq in st.session_state.equipamentos:
                st.write("🔹 **[" + str(eq['id']) + "] " + str(eq['nome']) + "** | Setor: " + str(eq['localizacao']) + " | Criticidade: " + str(eq['criticidade']))
                if st.button("🗑️ Remover " + str(eq['id']), key="del_" + str(eq['id'])):
                    st.session_state.equipamentos = [e for e in st.session_state.equipamentos if e['id'] != eq['id']]
                    st.success("Equipamento removido!")
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
            opcoes_edicao = {e['id'] + " - " + e['nome']: e for e in st.session_state.equipamentos}
            selecionado_edicao = st.selectbox("Selecione qual máquina deseja alterar:", list(opcoes_edicao.keys()))
            eq_para_editar = opcoes_edicao[selecionado_edicao]
            
            with st.form("form_edicao"):
                novo_nome = st.text_input("Nome do Equipamento:", value=eq_para_editar['nome'])
                novo_local = st.text_input("Localização / Setor:", value=eq_para_editar['localizacao'])
                novo_crit = st.selectbox("Criticidade:", ["Baixa", "Média", "Alta"], index=["Baixa", "Média", "Alta"].index(eq_para_editar['criticidade']))
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
# 2. PLANEJAMENTO TEMPORAL
# ==========================================
elif menu == "📅 Planejamento & Checklists":
    st.header("📅 Planejamento de Manutenções Preventivas")
    aba_sem, aba_mes, aba_ano, aba_novo = st.tabs(["🗓️ Semanal", "📅 Mensal", "⏳ Anual", "➕ Agendar Preventiva"])
    
    def exibir_itens(frequencia, chave_check):
        dados = [p for p in st.session_state.planejamento if p['periodo'] == frequencia and p['status'] == "Pendente"]
        if dados:
            for p in dados:
                st.write("⚙️ **" + str(p['equipamento']) + "** | 📅 **Data:** " + str(p.get('data_prevista')) + " | **Status:** " + str(p['status']))
                st.write("🔧 Peças Programadas: " + str(p['pecas']))
                st.write("---")
        else:
            st.info("Nenhuma manutenção pendente para " + str(frequencia) + ".")

    with aba_sem: exibir_itens("Semanal", "check_semanal")
    with aba_mes: exibir_itens("Mensal", "check_mensal")
    with aba_ano: exibir_itens("Anual", "check_anual")
    
    with aba_novo:
        st.subheader("📋 Agendar Nova Preventiva")
        lista_nomes = [e['nome'] for e in st.session_state.equipamentos]
        
        if not lista_nomes:
            st.warning("Cadastre uma máquina primeiro.")
        else:
            eq_escolhido = st.selectbox("Selecione a Máquina Alvo:", lista_nomes, key="plan_eq")
            periodo_escolhido = st.selectbox("Escolha o Período:", ["Semanal", "Mensal", "Anual"], key="plan_per")
            data_planejada = st.date_input("Selecione a Data do Serviço:", datetime.now(), key="plan_data")
            pecas_necessarias = st.text_area("Descrição das Peças:", key="plan_pecas")
            regras_seguranca = st.text_area("Instruções de Segurança:", value="Uso de EPIs obrigatório. Lockout/Tagout.", key="plan_seg")
            
            if st.button("💾 Gravar Agendamento", key="btn_gravar_preventiva"):
                nova_os = {
                    "id": len(st.session_state.planejamento) + 1,
                    "equipamento": eq_escolhido,
                    "periodo": periodo_escolhido,
                    "data_prevista": data_planejada.strftime('%d/%m/%Y'),
                    "pecas": pecas_necessarias,
                    "status": "Pendente",
                    "seguranca": rules_seguranca if 'rules_seguranca' in locals() else regras_seguranca
                }
                st.session_state.planejamento.append(nova_os)
                st.success("Manutenção agendada com sucesso!")
                st.rerun()

# ==========================================
# 3. HISTÓRICO DE TROCAS
# ==========================================
elif menu == "📜 Histórico de Trocas":
    st.header("📜 Histórico de Manutenções Realizadas")
    if not st.session_state.historico:
        st.info("Nenhum registro encontrado no histórico.")
    else:
        for h in st.session_state.historico:
            st.success("📅 **Data:** " + str(h['data']) + " | ⚙️ **Máquina:** " + str(h['equipamento']) + " | <b> Executor:</b> " + str(h['executor']))
            st.write("📌 **Tipo:** " + str(h['tipo']) + " | 🔄 **Peças Substituídas:** " + str(h['pecas_trocadas']))
            st.write("---")

# ==========================================
# 4. EMISSÃO DE PT (BLINDAGEM CONTRA INDENTAÇÃO)
# ==========================================
elif menu == "⚠️ Emissão de PT":
    st.header("⚠️ Emissão e Impressão de Permissão de Trabalho (PT)")
    
    # Busca linear sem blocos condicionais aninhados (Imune a erros de espaço no else)
    ordens_pendentes = [p for p in st.session_state.planejamento if p.get("status") == "Pendente"]
    
