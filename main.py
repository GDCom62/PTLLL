import streamlit as st
from datetime import datetime
import os
import json
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Controle de Manutenção & PT", layout="wide", page_icon="⚙️")

# --- BANCO DE DADOS PERSISTENTE EM ARQUIVO LOCAL (JSON) ---
ARQUIVO_BANCO = "banco_manutencao.json"

def carregar_dados():
    """Carrega os dados do arquivo local. Se chaves estiverem vazias, injeta os dados reais."""
    dados_padrao = {
        "maquinas": [
            {"id": "EQ-001", "nome": "Torno Mecânico Nardini", "localizacao": "Oficina Central", "criticidade": "Alta", "check_semanal": "1. Verificar nível de óleo; 2. Limpar barramento.", "check_mensal": "1. Trocar filtros; 2. Conferir correias.", "check_anual": "1. Revisão do motor."},
            {"id": "EQ-002", "nome": "Compressor de Ar Schulz", "localizacao": "Sala de Compressores", "criticidade": "Média", "check_semanal": "1. Drenar reservatório; 2. Checar ruídos.", "check_mensal": "1. Limpar filtro; 2. Verificar conexões.", "check_anual": "1. Teste de válvula."}
        ],
        "planejamento": [
            {"id": 1, "equipamento": "Torno Mecânico Nardini", "periodo": "Semanal", "data_prevista": datetime.now().strftime("%d/%m/%Y"), "pecas": "Troca de óleo das guias e limpeza", "status": "Pendente", "seguranca": "Cuidado com partes giratórias."}
        ],
        "historico": [
            {"id": 99, "equipamento": "Compressor de Ar Schulz", "periodo": "Mensal", "data_prevista": "15/05/2026", "data_conclusao": "15/05/2026 10:00", "pecas": "Troca de filtro de ar", "status": "Concluido"}
        ]
    }

    if os.path.exists(ARQUIVO_BANCO):
        try:
            with open(ARQUIVO_BANCO, "r", encoding="utf-8") as f:
                conteudo = json.load(f)
                
                # --- BLINDAGEM DA RECUPERAÇÃO OPERACIONAL ---
                # Se o arquivo existir, garante que nenhuma lista interna venha nula ou vazia
                if not conteudo or not isinstance(conteudo, dict):
                    conteudo = dados_padrao
                if "maquinas" not in conteudo or not conteudo["maquinas"]:
                    conteudo["maquinas"] = dados_padrao["maquinas"]
                if "planejamento" not in conteudo or not conteudo["planejamento"]:
                    conteudo["planejamento"] = dados_padrao["planejamento"]
                if "historico" not in conteudo or not conteudo["historico"]:
                    conteudo["historico"] = dados_padrao["historico"]
                    
                return conteudo
        except Exception:
            pass
            
    with open(ARQUIVO_BANCO, "w", encoding="utf-8") as f:
        json.dump(dados_padrao, f, ensure_ascii=False, indent=4)
    return dados_padrao

def salvar_dados_físicos():
    """Grava o estado atual da memória diretamente no arquivo JSON permanente."""
    dados_para_salvar = {
        "maquinas": st.session_state.maquinas,
        "planejamento": st.session_state.planejamento,
        "historico": st.session_state.historico
    }
    with open(ARQUIVO_BANCO, "w", encoding="utf-8") as f:
        json.dump(dados_para_salvar, f, ensure_ascii=False, indent=4)

# Inicialização e sincronização imediata
db_inicial = carregar_dados()
st.session_state.maquinas = db_inicial["maquinas"]
st.session_state.planejamento = db_inicial["planejamento"]
st.session_state.historico = db_inicial["historico"]

# Estados de controle para edição
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

equipamentos = st.session_state.maquinas
todos_agendamentos = st.session_state.planejamento
historico_lista = st.session_state.historico

# ==========================================
# ABAS 1 & 2: GERENCIAR MÁQUINAS (SUA ABA QUE JÁ FUNCIONA)
# ==========================================
if menu == "🔍 Abas 1 & 2: Gerenciar Máquinas":
    st.header("🔍 Gerenciamento de Equipamentos")
    
    if st.session_state.editando_maquina_id is not None:
        st.subheader("✏️ Editar Equipamento Registrado")
        mq_editar = next((m for m in st.session_state.maquinas if m["id"] == st.session_state.editando_maquina_id), None)
        
        if mq_editar:
            with st.form("form_editar_maquina"):
                edit_nome = st.text_input("Nome do Equipamento:", value=mq_editar["nome"])
                edit_local = st.text_input("Localização / Setor:", value=mq_editar["localizacao"])
                edit_crit = st.selectbox("Criticidade:", ["Baixa", "Média", "Alta"], index=["Baixa", "Média", "Alta"].index(mq_editar["criticidade"]))
                edit_sem = st.text_area("Checklist Semanal:", value=mq_editar["check_semanal"])
                edit_mes = st.text_area("Checklist Mensal:", value=mq_editar["check_mensal"])
                edit_ano = st.text_area("Checklist Anual:", value=mq_editar["check_anual"])
                
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    btn_salvar_mq = st.form_submit_button("💾 Salvar Alterações")
                with col_m2:
                    btn_canc_mq = st.form_submit_button("❌ Cancelar")
                
            if btn_salvar_mq:
                mq_editar["nome"] = edit_nome
                mq_editar["localizacao"] = edit_local
                mq_editar["criticidade"] = edit_crit
                mq_editar["check_semanal"] = edit_sem
                mq_editar["check_mensal"] = edit_mes
                mq_editar["check_anual"] = edit_ano
                st.session_state.editando_maquina_id = None
                salvar_dados_físicos()
                st.success("Equipamento atualizado com sucesso!")
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
            st.session_state.maquinas.append({"id": id_eq, "nome": nome_eq, "localizacao": local_eq, "criticidade": crit_eq, "check_semanal": c_sem, "check_mensal": c_mes, "check_anual": c_ano})
            salvar_dados_físicos()
            st.success("Equipamento cadastrado e gravado com sucesso!")
            st.rerun()

    st.markdown("---")
    st.subheader("📋 Lista de Equipamentos Registrados")
    if not st.session_state.maquinas:
        st.info("Nenhuma máquina cadastrada no momento.")
    else:
        for mq in st.session_state.maquinas:
            st.write(f"🔹 **[{mq['id']}] {mq['nome']}** | Setor: {mq['localizacao']} | Criticidade: {mq['criticidade']}")
            c_m1, c_m2 = st.columns(2)
            with c_m1:
                if st.button(f"✏️ Editar {mq['id']}", key=f"ed_mq_{mq['id']}"):
                    st.session_state.editando_maquina_id = mq['id']
                    st.rerun()
            with c_m2:
                if st.button(f"🗑️ Excluir {mq['id']}", key=f"ex_mq_{mq['id']}"):
                    st.session_state.maquinas = [m for m in st.session_state.maquinas if m["id"] != mq["id"]]
                    salvar_dados_físicos()
                    st.warning("Equipamento excluído com sucesso!")
                    st.rerun()
            st.write("---")

# ==========================================
# ABA 3: PLANEJAMENTO E ORDENS DE SERVIÇO (OS)
# ==========================================
elif menu == "📅 Aba 3: Ordens de Serviço (OS)":
    st.header("📅 Planejamento & Ordens de Serviço (OS)")
    
    if st.session_state.editando_os_id is not None:
        st.subheader("📝 Editar Ordem de Serviço Ativa")
        os_editar = next((item for item in st.session_state.planejamento if item["id"] == st.session_state.editando_os_id), None)
        
        if os_editar:
            with st.form("form_editar_os"):
                edit_equip = st.selectbox("Máquina Alvo:", [m["nome"] for m in st.session_state.maquinas], index=[m["nome"] for m in st.session_state.maquinas].index(os_editar["equipamento"]) if os_editar["equipamento"] in [m["nome"] for m in st.session_state.maquinas] else 0)
                edit_periodo = st.selectbox("Escolha o Período:", ["Semanal", "Mensal", "Anual"], index=["semanal", "mensal", "anual"].index(os_editar["periodo"].lower()))
                edit_data = st.date_input("Data Prevista:", datetime.strptime(os_editar["data_prevista"], "%d/%m/%Y"))
                edit_pecas = st.text_area("Escopo do Serviço:", value=os_editar["pecas"])
                edit_seg = st.text_area("Observações de Segurança:", value=os_editar.get("seguranca", ""))
                
                col_b1, col_b2 = st.columns(2)
                with col_b1:
                    btn_salvar_os = st.form_submit_button("💾 Salvar OS")
                with col_b2:
                    btn_canc_os = st.form_submit_button("❌ Cancelar")
                
