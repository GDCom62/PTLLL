import streamlit as st
from datetime import datetime
import pandas as pd
import requests

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Controle de Manutenção & PT", layout="wide", page_icon="⚙️")

# --- CONEXÃO COM O SUPABASE VIA REST API ---
def obter_credenciais():
    try:
        url = st.secrets["supabase"]["url"].strip().rstrip("/")
        key = st.secrets["supabase"]["key"].strip()
        return url, key
    except Exception as e:
        st.error(f"Erro ao ler os Secrets no Streamlit: {e}")
        return None, None

SUBAPASE_URL, SUPABASE_KEY = obter_credenciais()

def buscar_dados(tabela: str):
    if not SUBAPASE_URL or not SUPABASE_KEY:
        return []
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    url = f"{SUBAPASE_URL}/rest/v1/{tabela}?select=*"
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return []

def inserir_dados(tabela: str, payload: dict):
    if not SUBAPASE_URL or not SUPABASE_KEY:
        return False
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    url = f"{SUBAPASE_URL}/rest/v1/{tabela}"
    try:
        response = requests.post(url, headers=headers, json=payload)
        return 200 <= response.status_code <= 299
    except Exception:
        return False

def atualizar_dados(tabela: str, payload: dict, coluna_id: str, valor_id):
    if not SUBAPASE_URL or not SUPABASE_KEY:
        return False
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    url = f"{SUBAPASE_URL}/rest/v1/{tabela}?{coluna_id}=eq.{valor_id}"
    try:
        response = requests.patch(url, headers=headers, json=payload)
        return 200 <= response.status_code <= 299
    except Exception:
        return False

def excluir_dados(tabela: str, coluna_id: str, valor_id):
    if not SUBAPASE_URL or not SUPABASE_KEY:
        return False
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    url = f"{SUBAPASE_URL}/rest/v1/{tabela}?{coluna_id}=eq.{valor_id}"
    try:
        response = requests.delete(url, headers=headers)
        return 200 <= response.status_code <= 299
    except Exception:
        return False

# --- CONTROLE DE ESTADOS ---
if "editando_maquina_id" not in st.session_state:
    st.session_state.editando_maquina_id = None

# --- MENU LATERAL ---
st.sidebar.markdown("**Desenvolvido por GDCOM**")
st.sidebar.title("⚙️ Gestão de Manutenção")
menu = st.sidebar.radio("Navegar para:", ["🔍 Abas 1 & 2: Gerenciar Máquinas"])

# Carga de dados ao vivo direto do banco
equipamentos = buscar_dados("maquinas")

# Lista reserva local apenas se o banco estiver inacessível ou falhar temporariamente
if not equipamentos:
    equipamentos = [
        {"id": "EQ-001", "nome": "Torno Mecânico Nardini", "localizacao": "Oficina Central", "criticidade": "Alta", "check_semanal": "1. Óleo", "check_mensal": "1. Filtro", "check_anual": "1. Motor"},
        {"id": "EQ-002", "nome": "Compressor de Ar Schulz", "localizacao": "Sala Compressores", "criticidade": "Média", "check_semanal": "1. Drenar", "check_mensal": "1. Limpar", "check_anual": "1. Válvula"}
    ]

# --- INTERFACE ABA 1 & 2 ---
st.header("🔍 Gerenciamento de Equipamentos")

if st.session_state.editando_maquina_id is not None:
    st.subheader("✏️ Editar Equipamento Registrado")
    mq_editar = next((m for m in equipamentos if str(m["id"]) == str(st.session_state.editando_maquina_id)), None)
    
    if mq_editar:
        with st.form("form_editar_maquina"):
            edit_id = st.text_input("Tag do Equipamento (Não altere):", value=str(mq_editar.get("id", "")), disabled=True)
            edit_nome = st.text_input("Nome do Equipamento:", value=mq_editar.get("nome", ""))
            edit_local = st.text_input("Localização / Setor:", value=mq_editar.get("localizacao", ""))
            edit_crit = st.selectbox("Criticidade:", ["Baixa", "Média", "Alta"], index=["Baixa", "Média", "Alta"].index(mq_editar.get("criticidade", "Baixa")))
            edit_sem = st.text_area("Checklist Semanal:", value=mq_editar.get("check_semanal", ""))
            edit_mes = st.text_area("Checklist Mensal:", value=mq_editar.get("check_mensal", ""))
            edit_ano = st.text_area("Checklist Anual:", value=mq_editar.get("check_anual", ""))
            
            btn_salvar_mq = st.form_submit_button("💾 Salvar Alterações")
            btn_canc_mq = st.form_submit_button("❌ Cancelar")
            
        if btn_salvar_mq:
            # Payload correto contendo a amarração sem violar a chave primária
            payload = {
                "nome": edit_nome, 
                "localizacao": edit_local, 
                "criticidade": edit_crit, 
                "check_semanal": edit_sem, 
                "check_mensal": edit_mes, 
                "check_anual": edit_ano
            }
            sucesso = atualizar_dados("maquinas", payload, "id", mq_editar["id"])
            if sucesso:
                st.success("🎉 Alterações salvas com sucesso no Supabase!")
                st.session_state.editando_maquina_id = None
                st.rerun()
            else:
                st.error("Falha ao salvar no banco de dados. Certifique-se de que a tabela aceita gravações externas.")
                
        if btn_canc_mq:
            st.session_state.editando_maquina_id = None
            st.rerun()
else:
    st.subheader("➕ Cadastrar Nova Máquina")
    with st.form("form_cadastro_direto"):
        id_eq = st.text_input("Tag do Equipamento (Ex: EQ-003):").strip()
        nome_eq = st.text_input("Nome do Equipamento:").strip()
        local_eq = st.text_input("Localização / Setor:")
        crit_eq = st.selectbox("Criticidade:", ["Baixa", "Média", "Alta"])
        c_sem = st.text_area("Checklist Semanal:", "1. Verificar nível de óleo; 2. Limpeza.")
        c_mes = st.text_area("Checklist Mensal:", "1. Troca de filtros.")
        c_ano = st.text_area("Checklist Anual:", "1. Revisão preventiva.")
        botao_salvar = st.form_submit_button("Salvar Novo Equipamento")
        
    if botao_salvar:
        if not id_eq or not nome_eq:
            st.error("Por favor, preencha obrigatoriamente a Tag (ID) e o Nome do Equipamento.")
        else:
            payload = {
                "id": id_eq, 
                "nome": nome_eq, 
                "localizacao": local_eq, 
                "criticidade": crit_eq, 
                "check_semanal": c_sem, 
                "check_mensal": c_mes, 
                "check_anual": c_ano
            }
            sucesso = inserir_dados("maquinas", payload)
            if sucesso:
                st.success("🎉 Equipamento gravado com sucesso no Supabase!")
                st.rerun()
            else:
                st.error("Erro ao inserir dados no Supabase. Verifique se essa Tag já não existe no banco.")

st.markdown("---")
st.subheader("📋 Lista de Equipamentos Registrados")
for mq in equipamentos:
    st.write(f"🔹 **[{mq.get('id')}] {mq.get('nome')}** | Setor: {mq.get('localizacao')} | Criticidade: {mq.get('criticidade')}")
    
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        if st.button(f"✏️ Editar {mq.get('id')}", key=f"ed_mq_{mq.get('id')}"):
            st.session_state.editando_maquina_id = mq.get('id')
            st.rerun()
    with col_b2:
        if st.button(f"🗑️ Excluir {mq.get('id')}", key=f"ex_mq_{mq.get('id')}"):
            sucesso_ex = excluir_dados("maquinas", "id", mq.get('id'))
            if sucesso_ex:
                st.warning("Equipamento excluído com sucesso do Supabase!")
                st.rerun()
            else:
                st.error("Erro ao tentar excluir o equipamento no banco.")
                
    st.write("---")
