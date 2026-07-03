import streamlit as st
from datetime import datetime
import pandas as pd
import requests

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Controle de Manutenção & PT", layout="wide", page_icon="⚙️")

# --- CONEXÃO BLINDADA VIA API REST (HTTP) COM O SUPABASE ---
@st.cache_resource
def obter_credenciais():
    """Recupera e limpa as credenciais dos Secrets."""
    try:
        url = st.secrets["supabase"]["url"].strip().rstrip("/")
        key = st.secrets["supabase"]["key"].strip()
        return url, key
    except Exception as e:
        st.error(f"Erro ao ler os Secrets no Streamlit: {e}")
        return None, None

SUBAPASE_URL, SUPABASE_KEY = obter_credenciais()

# --- FUNÇÕES DE INTERAÇÃO DIRETA COM O BANCO DE DADOS (API REST) ---
def buscar_dados(tabela: str):
    """Busca dados diretamente via REST API do Supabase."""
    if not SUBAPASE_URL or not SUPABASE_KEY:
        return []
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }
    url = f"{SUBAPASE_URL}/rest/v1/{tabela}?select=*"
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return []

def inserir_dados(tabela: str, payload: dict):
    """Insere um novo registro diretamente via REST API."""
    if not SUBAPASE_URL or not SUPABASE_KEY:
        return False
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }
    url = f"{SUBAPASE_URL}/rest/v1/{tabela}"
    try:
        response = requests.post(url, headers=headers, json=payload)
        return 200 <= response.status_code <= 299
    except Exception:
        return False

def atualizar_dados(tabela: str, payload: dict, coluna_id: str, valor_id):
    """Atualiza um registro diretamente via REST API."""
    if not SUBAPASE_URL or not SUPABASE_KEY:
        return False
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }
    url = f"{SUBAPASE_URL}/rest/v1/{tabela}?{coluna_id}=eq.{valor_id}"
    try:
        response = requests.patch(url, headers=headers, json=payload)
        return 200 <= response.status_code <= 299
    except Exception:
        return False

def excluir_dados(tabela: str, coluna_id: str, valor_id):
    """Exclui um registro diretamente via REST API."""
    if not SUBAPASE_URL or not SUPABASE_KEY:
        return False
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }
    url = f"{SUBAPASE_URL}/rest/v1/{tabela}?{coluna_id}=eq.{valor_id}"
    try:
        response = requests.delete(url, headers=headers)
        return 200 <= response.status_code <= 299
    except Exception:
        return False

# Estados de controle para edição ativa
if "editando_maquina_id" not in st.session_state:
    st.session_state.editando_maquina_id = None
if "editando_os_id" not in st.session_state:
    st.session_state.editando_os_id = None

# --- MENU LATERAL ---
st.sidebar.markdown("**Desenvolvido por GDCOM**")
st.sidebar.title("⚙️ Gestão de Manutenção")
menu = st.sidebar.radio("Navegar para:", [
    "🔍 Abas 1 & 2: Gerenciar Máquinas",
    "📅 Aba 3: Ordens de Serviço (OS)",
    "📜 Aba 4: Histórico de Trocas",
    "⚠️ Aba 5: Emissão de PT"
])

# Carregamento dinâmico e direto das tabelas estruturadas
equipamentos = buscar_dados("maquinas")
todos_agendamentos = buscar_dados("planejamento")
historico_lista = buscar_dados("historico")

# Injeção local de segurança caso o banco retorne vazio para evitar telas em branco
if not equipamentos:
    equipamentos = [
        {"id": "EQ-001", "nome": "Torno Mecânico Nardini", "localizacao": "Oficina Central", "criticidade": "Alta", "check_semanal": "1. Verificar nível de óleo.", "check_mensal": "1. Trocar filtros.", "check_anual": "1. Revisão motor."},
        {"id": "EQ-002", "nome": "Compressor de Ar Schulz", "localizacao": "Sala Compressores", "criticidade": "Média", "check_semanal": "1. Drenar reservatório.", "check_mensal": "1. Limpar conexões.", "check_anual": "1. Teste válvula."}
    ]

if not todos_agendamentos:
    todos_agendamentos = [
        {"id": 1, "equipamento": "Torno Mecânico Nardini", "periodo": "Semanal", "data_prevista": datetime.now().strftime("%d/%m/%Y"), "pecas": "Troca de óleo das guias e limpeza", "status": "Pendente", "seguranca": "Cuidado com partes giratórias."}
    ]

# ==========================================
# ABAS 1 & 2: GERENCIAR MÁQUINAS
# ==========================================
if menu == "🔍 Abas 1 & 2: Gerenciar Máquinas":
    st.header("🔍 Gerenciamento de Equipamentos")
    
    if st.session_state.editando_maquina_id is not None:
        st.subheader("✏️ Editar Equipamento Registrado")
        mq_editar = next((m for m in equipamentos if str(m["id"]) == str(st.session_state.editando_maquina_id)), None)
        
        if mq_editar:
            with st.form("form_editar_maquina"):
                edit_nome = st.text_input("Nome do Equipamento:", value=mq_editar.get("nome", ""))
                edit_local = st.text_input("Localização / Setor:", value=mq_editar.get("localizacao", ""))
                edit_crit = st.selectbox("Criticidade:", ["Baixa", "Média", "Alta"], index=["Baixa", "Média", "Alta"].index(mq_editar.get("criticidade", "Baixa")))
                edit_sem = st.text_area("Checklist Semanal:", value=mq_editar.get("check_semanal", ""))
                edit_mes = st.text_area("Checklist Mensal:", value=mq_editar.get("check_mensal", ""))
                edit_ano = st.text_area("Checklist Anual:", value=mq_editar.get("check_anual", ""))
                
                col_m1, col_m2 = st.columns(2)
                with col_m1: btn_salvar_mq = st.form_submit_button("💾 Salvar Alterações")
                with col_m2: btn_canc_mq = st.form_submit_button("❌ Cancelar")
                
            if btn_salvar_mq:
                payload = {"nome": edit_nome, "localizacao": edit_local, "criticidade": edit_crit, "check_semanal": edit_sem, "check_mensal": edit_mes, "check_anual": edit_ano}
                atualizar_dados("maquinas", payload, "id", mq_editar["id"])
                st.session_state.editando_maquina_id = None
                st.success("🎉 Equipamento atualizado com sucesso no Supabase!")
                st.rerun()
            if btn_canc_mq:
                st.session_state.editando_maquina_id = None
                st.rerun()
    else:
        st.subheader("➕ Cadastrar Nova Máquina")
        with st.form("form_cadastro_direto"):
            id_eq = st.text_input("Tag do Equipamento (Ex: EQ-003):")
            nome_eq = st.text_input("Nome do Equipamento:")
            local_eq = st.text_input("Localização / Setor:")
            crit_eq = st.selectbox("Criticidade:", ["Baixa", "Média", "Alta"])
            st.markdown("##### 📜 Ações Preventivas")
            c_sem = st.text_area("Checklist Semanal:", "1. Verificar nível de óleo; 2. Limpeza.")
            c_mes = st.text_area("Checklist Mensal:", "1. Troca de filtros.")
            c_ano = st.text_area("Checklist Anual:", "1. Revisão preventiva.")
            botao_salvar = st.form_submit_button("Salvar Novo Equipamento")
            
        if botao_salvar and id_eq and nome_eq:
            payload = {"id": id_eq, "nome": nome_eq, "localizacao": local_eq, "criticidade": crit_eq, "check_semanal": c_sem, "check_mensal": c_mes, "check_anual": c_ano}
            inserir_dados("maquinas", payload)
            st.success("🎉 Equipamento salvo diretamente no Supabase!")
            st.rerun()

    st.markdown("---")
    st.subheader("📋 Lista de Equipamentos Registrados")
    for mq in equipamentos:
        st.write(f"🔹 **[{mq.get('id')}] {mq.get('nome')}** | Setor: {mq.get('localizacao')} | Criticidade: {mq.get('criticidade')}")
        c_m1, c_m2 = st.columns(2)
        with c_m1:
            if st.button(f"✏️ Editar {mq.get('id')}", key=f"ed_mq_{mq.get('id')}"):
                st.session_state.editando_maquina_id = mq.get('id')
                st.rerun()
        with c_m2:
            if st.button(f"🗑️ Excluir {mq.get('id')}", key=f"ex_mq_{mq.get('id')}"):
                excluir_dados("maquinas", "id", mq.get('id'))
                st.warning("Equipamento excluído permanentemente!")
                st.rerun()
        st.write("---")

# ==========================================
# ABA 3: PLANEJAMENTO E ORDENS DE SERVIÇO (OS)
# ==========================================
elif menu == "📅 Aba 3: Ordens de Serviço (OS)":
    st.header("📅 Planejamento & Ordens de Serviço (OS)")
    
    if st.session_state.editando_os_id is not None:
        st.subheader("📝 Editar Ordem de Serviço Ativa")
        os_editar = next((item for item in todos_agendamentos if str(item["id"]) == str(st.session_state.editando_os_id)), None)
        
        if os_editar:
            with st.form("form_editar_os"):
                edit_equip = st.selectbox("Máquina Alvo:", [m["nome"] for m in equipamentos], index=[m["nome"] for m in equipamentos].index(os_editar["equipamento"]) if os_editar["equipamento"] in [m["nome"] for m in equipamentos] else 0)
                edit_periodo = st.selectbox("Escolha o Período:", ["Semanal", "Mensal", "Anual"], index=["semanal", "mensal", "anual"].index(os_editar.get("periodo", "Semanal").lower()))
                edit_data = st.date_input("Data Prevista:", datetime.strptime(os_editar.get("data_prevista", datetime.now().strftime("%d/%m/%Y")), "%d/%m/%Y"))
                edit_pecas = st.text_area("Escopo do Serviço:", value=os_editar.get("pecas", ""))
                edit_seg = st.text_area("Observações de Segurança:", value=os_editar.get("seguranca", ""))
                
                col_b1, col_b2 = st.columns(2)
