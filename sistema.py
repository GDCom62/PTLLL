import streamlit as st
import json
import os
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Controle de Manutenção & PT", layout="wide", page_icon="⚙️")

# --- ARQUIVOS DE ARMAZENAMENTO REAL (NÃO APAGA MAIS) ---
ARQUIVO_EQ = "dados_equipamentos.json"
ARQUIVO_PLAN = "dados_planejamento.json"
ARQUIVO_HIST = "dados_historico.json"

# --- FUNÇÕES DE CARGA E SALVAMENTO AUTOMÁTICO ---
def carregar_dados(arquivo, dados_padrao):
    if os.path.exists(arquivo):
        try:
            with open(arquivo, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return dados_padrao
    return dados_padrao

def salvar_dados(arquivo, dados):
    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

# --- INICIALIZAÇÃO FIXA EM STATE ---
if "equipamentos" not in st.session_state:
    st.session_state.equipamentos = carregar_dados(ARQUIVO_EQ, [
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
    ])

if "planejamento" not in st.session_state:
    st.session_state.planejamento = carregar_dados(ARQUIVO_PLAN, [])

if "historico" not in st.session_state:
    st.session_state.historico = carregar_dados(ARQUIVO_HIST, [])

# --- INJEÇÃO DA MARCA DIGITAL NO CANTO INFERIOR DIREITO (BLINDADO - SEM DEPENDER DE IMAGEM) ---
st.markdown(
    """
    <div style="position: fixed; bottom: 10px; right: 10px; z-index: 9999; display: flex; align-items: center; background-color: rgba(255,255,255,0.8); padding: 4px 8px; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.2); pointer-events: none;">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#FF4B4B" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 5px;"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><line x1="9" y1="9" x2="15" y2="15"></line><line x1="15" y1="9" x2="9" y2="15"></line></svg>
        <span style="font-size: 11px; font-family: sans-serif; font-weight: bold; color: #333; letter-spacing: 0.5px;">DGCOM</span>
    </div>
    """,
    unsafe_allow_html=True
)

# --- MENU LATERAL DE NAVEGAÇÃO ---
st.sidebar.markdown("<h2 style='color:#FF4B4B; margin-top:0;'>⚙️ DGCOM</h2>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='font-size:12px; color:gray; margin-top:-15px;'>Sistema de Gestão Industrial</p>", unsafe_allow_html=True)

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
        for eq in st.session_state.equipamentos:
            st.write(f"🔹 **[{eq['id']}] {eq['nome']}** | Setor: {eq['localizacao']} | Criticidade: {eq['criticidade']}")
            if st.button(f"🗑️ Remover {eq['id']}", key=f"del_{eq['id']}"):
                st.session_state.equipamentos = [e for e in st.session_state.equipamentos if e['id'] != eq['id']]
                salvar_dados(ARQUIVO_EQ, st.session_state.equipamentos)
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
                        salvar_dados(ARQUIVO_EQ, st.session_state.equipamentos)
                        st.success("Máquina registrada e salva com sucesso!")
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
                    salvar_dados(ARQUIVO_EQ, st.session_state.equipamentos)
                    st.success("Alterações salvas!")
                    st.rerun()

# ==========================================
# 2. PLANEJAMENTO TEMPORAL (TOTALMENTE RECONSTRUÍDO)
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
        
