import streamlit as st
import subprocess
import sys

# --- INSTALADOR AUTOMÁTICO INTEGRADO (CORREÇÃO DO MODULE_NOT_FOUND) ---
try:
    from supabase import create_client, Client
except ModuleNotFoundError:
    # Força a instalação imediata direto no servidor do Streamlit Cloud
    subprocess.check_call([sys.executable, "-m", "pip", "install", "supabase==2.4.6", "postgrest==0.16.4"])
    from supabase import create_client, Client

from datetime import datetime
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Controle de Manutenção & PT", layout="wide", page_icon="⚙️")

# --- CONEXÃO NATIVA COM O BANCO DE DADOS SUPABASE ---
@st.cache_resource
def inicializar_supabase() -> Client:
    """Estabelece a conexão com a API do Supabase usando os Secrets salvos na nuvem."""
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        return create_client(url, key)
    except Exception as e:
        st.error(f"Erro ao conectar com o Supabase. Verifique os Secrets no Streamlit: {e}")
        return None

supabase = inicializar_supabase()

# --- FUNÇÕES DE SINCRONIZAÇÃO E GRAVAÇÃO EM TEMPO REAL ---
def buscar_dados(tabela: str):
    """Busca os dados de uma tabela específica no Supabase. Retorna uma lista de dicionários."""
    if supabase:
        try:
            resposta = supabase.table(tabela).select("*").execute()
            return resposta.data if respuesta.data else []
        except Exception:
            return []
    return []

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

# Carregamento dinâmico direto das tabelas do Supabase
equipamentos = buscar_dados("maquinas")
todos_agendamentos = buscar_dados("planejamento")
historico_lista = buscar_dados("historico")

# ==========================================
# ABAS 1 & 2: GERENCIAR MÁQUINAS
# ==========================================
if menu == "🔍 Abas 1 & 2: Gerenciar Máquinas":
    st.header("🔍 Gerenciamento de Equipamentos")
    
    if st.session_state.editando_maquina_id is not None:
        st.subheader("✏️ Editar Equipamento Registrado")
        mq_editar = next((m for m in equipamentos if m["id"] == st.session_state.editando_maquina_id), None)
        
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
                
            if btn_salvar_mq and supabase:
                payload = {"nome": edit_nome, "localizacao": edit_local, "criticidade": edit_crit, "check_semanal": edit_sem, "check_mensal": edit_mes, "check_anual": edit_ano}
                supabase.table("maquinas").update(payload).eq("id", mq_editar["id"]).execute()
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
            
        if botao_salvar and id_eq and nome_eq and supabase:
            payload = {"id": id_eq, "nome": nome_eq, "localizacao": local_eq, "criticidade": crit_eq, "check_semanal": c_sem, "check_mensal": c_mes, "check_anual": c_ano}
            supabase.table("maquinas").insert(payload).execute()
            st.success("🎉 Equipamento salvo diretamente no Supabase!")
            st.rerun()

    st.markdown("---")
    st.subheader("📋 Lista de Equipamentos Registrados")
    if not equipamentos:
        st.info("Nenhuma máquina encontrada na tabela 'maquinas' do Supabase.")
    else:
        for mq in equipamentos:
            st.write(f"🔹 **[{mq.get('id')}] {mq.get('nome')}** | Setor: {mq.get('localizacao')} | Criticidade: {mq.get('criticidade')}")
            c_m1, c_m2 = st.columns(2)
            with c_m1:
                if st.button(f"✏️ Editar {mq.get('id')}", key=f"ed_mq_{mq.get('id')}"):
                    st.session_state.editando_maquina_id = mq.get('id')
                    st.rerun()
            with c_m2:
                if st.button(f"🗑️ Excluir {mq.get('id')}", key=f"ex_mq_{mq.get('id')}"):
                    if supabase:
                        supabase.table("maquinas").delete().eq("id", mq.get('id')).execute()
                        st.warning("Equipamento excluído permanentemente do Supabase!")
                        st.rerun()
            st.write("---")

# ==========================================
# ABA 3: PLANEJAMENTO E ORDENS DE SERVIÇO (OS)
# ==========================================
elif menu == "📅 Aba 3: Ordens de Serviço (OS)":
    st.header("📅 Planejamento & Ordens de Serviço (OS)")
    
    if st.session_state.editando_os_id is not None:
        st.subheader("📝 Editar Ordem de Serviço Ativa")
        os_editar = next((item for item in todos_agendamentos if item["id"] == st.session_state.editando_os_id), None)
        
        if os_editar:
            with st.form("form_editar_os"):
                edit_equip = st.selectbox("Máquina Alvo:", [m["nome"] for m in equipamentos], index=[m["nome"] for m in equipamentos].index(os_editar["equipamento"]) if os_editar["equipamento"] in [m["nome"] for m in equipamentos] else 0)
                edit_periodo = st.selectbox("Escolha o Período:", ["Semanal", "Mensal", "Anual"], index=["semanal", "mensal", "anual"].index(os_editar.get("periodo", "Semanal").lower()))
                edit_data = st.date_input("Data Prevista:", datetime.strptime(os_editar.get("data_prevista", datetime.now().strftime("%d/%m/%Y")), "%d/%m/%Y"))
                edit_pecas = st.text_area("Escopo do Serviço:", value=os_editar.get("pecas", ""))
                edit_seg = st.text_area("Observações de Segurança:", value=os_editar.get("seguranca", ""))
                
                col_b1, col_b2 = st.columns(2)
                with col_b1: btn_salvar_os = st.form_submit_button("💾 Salvar OS")
                with col_b2: btn_canc_os = st.form_submit_button("❌ Cancelar")
                
            if btn_salvar_os and supabase:
                payload = {"equipamento": edit_equip, "periodo": edit_periodo, "data_prevista": edit_data.strftime("%d/%m/%Y"), "pecas": edit_pecas, "seguranca": edit_seg}
                supabase.table("planejamento").update(payload).eq("id", os_editar["id"]).execute()
                st.session_state.editando_os_id = None
                st.success("🎉 Alterações na OS gravadas com sucesso!")
                st.rerun()
            if btn_canc_os:
                st.session_state.editando_os_id = None
                st.rerun()
    else:
        st.subheader("📅 Agendar Nova Manutenção / Gerar OS")
        with st.form("form_agenda_direto"):
            lista_nomes = [m["nome"] for m in equipamentos]
            eq_escolhido = st.selectbox("Selecione a Máquina Alvo:", lista_nomes if lista_nomes else ["Nenhum cadastrado"])
            periodo_escolhido = st.selectbox("Escolha o Período:", ["Semanal", "Mensal", "Anual"])
            data_planejada = st.date_input("Selecione a Data:", datetime.now())
            pecas_necessarias = st.text_area("Descrição das Peças / Escopo:", value="Realizar rotina padrão de preventiva.")
            seg_necessaria = st.text_area("Observações Iniciais de Segurança:", value="Seguir as NRs de segurança aplicadas.")
            botao_agenda = st.form_submit_button("💾 Gerar OS Pendente")
            
        if botao_agenda and eq_escolhido != "Nenhum cadastrado" and supabase:
            payload = {"equipamento": eq_escolhido, "periodo": periodo_escolhido, "data_prevista": data_planejada.strftime("%d/%m/%Y"), "pecas": pecas_necessarias, "status": "Pendente", "seguranca": seg_necessaria}
            supabase.table("planejamento").insert(payload).execute()
            st.success("🎉 Ordem de Serviço OS inserida e gravada com sucesso!")
            st.rerun()

    st.markdown("---")
