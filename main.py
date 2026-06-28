import streamlit as st
from datetime import datetime
import os
import requests
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Controle de Manutenção & PT", layout="wide", page_icon="⚙️")

# --- CONEXÃO DIRETA SUPABASE VIA API HTTP ---
SUB_URL = ""
SUB_HEADERS = {}
MODO_DEMO = False

try:
    if "SUPABASE_URL" in st.secrets and "SUPABASE_KEY" in st.secrets:
        SUB_URL = str(st.secrets["SUPABASE_URL"]).strip().rstrip("/")
        key_limpa = str(st.secrets["SUPABASE_KEY"]).strip()
        SUB_HEADERS = {
            "apikey": key_limpa,
            "Authorization": f"Bearer {key_limpa}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
    else:
        MODO_DEMO = True
except Exception as e:
    MODO_DEMO = True

# --- GARANTIA DA ESTRUTURA DE MEMÓRIA LOCAL DE BACKUP ---
if "maquinas_locais" not in st.session_state or not st.session_state.maquinas_locais:
    st.session_state.maquinas_locais = [
        {"id": "EQ-001", "nome": "Torno Mecânico Nardini", "localizacao": "Oficina Central", "criticidade": "Alta", "check_semanal": "Verificar nível de óleo, limpar barramento e lubrificar guias.", "check_mensal": "Trocar filtros de fluido, conferir tensão das correias.", "check_anual": "Revisão geral do motor elétrico e alinhamento geométrico."},
        {"id": "EQ-002", "nome": "Compressor de Ar Schulz", "localizacao": "Sala de Compressores", "criticidade": "Média", "check_semanal": "Drenar condensado do reservatório e checar ruídos estranhos.", "check_mensal": "Limpar/trocar filtro de ar, verificar vazamentos em conexões.", "check_anual": "Aferição do manômetro, teste de válvula de segurança e troca de óleo."}
    ]

if "planejamento_local" not in st.session_state or not st.session_state.planejamento_local:
    st.session_state.planejamento_local = [
        {"id": 1, "equipamento": "Torno Mecânico Nardini", "periodo": "Semanal", "data_prevista": datetime.now().strftime("%d/%m/%Y"), "pecas": "Inspeção preventiva padrão", "status": "Pendente"}
    ]

if "historico_local" not in st.session_state or not st.session_state.historico_local:
    st.session_state.historico_local = [
        {"id": 99, "equipamento": "Compressor de Ar Schulz", "periodo": "Mensal", "data_prevista": "15/05/2026", "data_conclusao": "15/05/2026 10:00", "pecas": "Troca de filtro de ar", "status": "Concluído"}
    ]

# --- MENU LATERAL AND LOGO GENERATION ---
if os.path.exists("logo.png"):
    st.sidebar.image("logo.png", use_column_width=True)
else:
    st.sidebar.info("💡 Para exibir sua logo, adicione o arquivo 'logo.png' no GitHub.")

st.sidebar.markdown("**Desenvolvido por GDCOM**")
st.sidebar.title("⚙️ Gestão de Manutenção")
menu = st.sidebar.radio("Navegar para:", [
    "🔍 Lista de Máquinas",
    "➕ Cadastrar Nova Máquina",
    "📅 Planejamento & Checklists",
    "📜 Histórico de Trocas",
    "⚠️ Emissão de PT"
])

# --- PUXA EQUIPAMENTOS DA NUVEM OU BACKUP ---
equipamentos = []
if not MODO_DEMO:
    try:
        req = requests.get(f"{SUB_URL}/rest/v1/equipamentos?select=*", headers=SUB_HEADERS, timeout=5)
        if req.status_code == 200 and isinstance(req.json(), list):
            equipamentos = req.json()
    except:
        pass
if not equipamentos or len(equipamentos) == 0:
    equipamentos = list(st.session_state.maquinas_locais)

# --- PUXA AGENDAMENTOS DA NUVEM OU BACKUP ---
todos_agendamentos = []
if not MODO_DEMO:
    try:
        req_plan = requests.get(f"{SUB_URL}/rest/v1/planejamento?status=eq.Pendente", headers=SUB_HEADERS, timeout=5)
        if req_plan.status_code == 200 and isinstance(req_plan.json(), list):
            todos_agendamentos = req_plan.json()
    except:
        pass

# AJUSTE SEGURO DEFINITIVO: Se a nuvem estiver vazia, obriga o preenchimento com o backup local
if not todos_agendamentos or len(todos_agendamentos) == 0:
    todos_agendamentos = list(st.session_state.planejamento_local)

# --- PUXA HISTÓRICO DA NUVEM OU BACKUP ---
historico_lista = []
if not MODO_DEMO:
    try:
        req_hist = requests.get(f"{SUB_URL}/rest/v1/historico?select=*", headers=SUB_HEADERS, timeout=5)
        if req_hist.status_code == 200 and isinstance(req_hist.json(), list):
            historico_lista = req_hist.json()
    except:
        pass
if not historico_lista or len(historico_lista) == 0:
    historico_lista = list(st.session_state.historico_local)

# ==========================================
# ABAS DO SISTEMA
# ==========================================
if menu == "🔍 Lista de Máquinas":
    st.header("🔍 Equipamentos Registrados")
    for idx, eq in enumerate(equipamentos):
        st.write(f"🔹 **[{eq.get('id', idx)}] {eq.get('nome', 'Equipamento')}** | Setor: {eq.get('localizacao', 'Geral')} | Criticidade: {eq.get('criticidade', 'Média')}")
        st.write("---")

elif menu == "➕ Cadastrar Nova Máquina":
    st.header("➕ Cadastrar Nova Máquina")
    with st.form("form_cadastro_direto"):
        id_eq = st.text_input("Código/Tag do Equipamento (Ex: EQ-003):")
        nome_eq = st.text_input("Nome do Equipamento:")
        local_eq = st.text_input("Localização / Setor:")
        crit_eq = st.selectbox("Criticidade:", ["Baixa", "Média", "Alta"])
        st.markdown("##### 📜 Ações Preventivas Recomendadas")
        c_sem = st.text_area("Checklist Semanal:", "Verificar nível de óleo\nLimpeza geral")
        c_mes = st.text_area("Checklist Mensal:", "Trocar filtros\nConferir correias")
        c_ano = st.text_area("Checklist Anual:", "Revisão geral do motor")
        botao_salvar = st.form_submit_button("Salvar Equipamento")
        
    if botao_salvar and id_eq and nome_eq:
        payload = {"id": id_eq, "nome": nome_eq, "localizacao": local_eq, "criticidade": crit_eq, "check_semanal": c_sem, "check_mes": c_mes, "check_anual": c_ano}
        if payload not in st.session_state.maquinas_locais:
            st.session_state.maquinas_locais.append(payload)
        if not MODO_DEMO:
            try:
                headers_g = SUB_HEADERS.copy()
                headers_g["Prefer"] = "resolution=merge-duplicates"
                requests.post(f"{SUB_URL}/rest/v1/equipamentos", json=payload, headers=headers_g, timeout=5)
            except: pass
        st.success("🎉 Equipamento e rotinas preventivas salvos com sucesso!")
        st.rerun()

elif menu == "📅 Planejamento & Checklists":
    st.header("📅 Planejamento de Manutenções Preventivas")
    
    st.subheader("📋 Consulta Rápida de Ações Preventivas")
    opcoes_lista = {eq.get('nome', 'Máquina'): eq for eq in equipamentos}
    maquina_selecionada = st.selectbox("Selecione uma máquina para ver suas ações preventivas padrão:", list(opcoes_lista.keys()))
    
    if maquina_selecionada:
        dados_mq = opcoes_lista[maquina_selecionada]
        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1: st.info(f"**Semanal:**\n{dados_mq.get('check_semanal', 'Não configurado.')}")
        with col_c2: st.warning(f"**Mensal:**\n{dados_mq.get('check_mes', 'Não configurado.')}")
        with col_c3: st.error(f"**Anual:**\n{dados_mq.get('check_anual', 'Não configurado.')}")
            
    st.markdown("---")
    st.subheader("📅 Agendar Nova Intervenção")
    with st.form("form_agenda_direto"):
        lista_nomes = list(opcoes_lista.keys())
        eq_escolhido = st.selectbox("Selecione a Máquina Alvo:", lista_nomes if lista_nomes else ["Nenhum cadastrado"])
        periodo_escolhido = st.selectbox("Escolha o Período:", ["Semanal", "Mensal", "Anual"])
        data_planejada = st.date_input("Selecione a Data:", datetime.now())
        pecas_necessarias = st.text_area("Descrição das Peças / Ferramentas / Escopo:", value="Realizar rotina padrão de preventiva.")
        botao_agenda = st.form_submit_button("💾 Gravar e Agendar Manutenção")
        
    if botao_agenda and eq_escolhido != "Nenhum cadastrado":
        novo_agendamento = {"id": len(todos_agendamentos) + 1, "equipamento": eq_escolhido, "periodo": periodo_escolhido, "data_prevista": data_planejada.strftime("%d/%m/%Y"), "pecas": pecas_necessarias, "status": "Pendente"}
        st.session_state.planejamento_local.append(novo_agendamento)
        if not MODO_DEMO:
            try: requests.post(f"{SUB_URL}/rest/v1/planejamento", json=novo_agendamento, headers=SUB_HEADERS, timeout=5)
            except: pass
        st.success("🎉 Agendamento registrado!")
        st.rerun()

    st.markdown("---")
    st.subheader("🔍 Ordens de Serviço Abertas")
    for idx, p in enumerate(todos_agendamentos):
        st.write(f"⚙️ **{p.get('equipamento')}** | Período: **{p.get('periodo')}** | 📅 **Prevista:** {p.get('data_prevista')}")
        st.write(f"🔧 Peças/Ferramentas: {p.get('pecas')}")
        if st.button("✔️ Concluir OS e Enviar para Histórico", key=f"comp_{idx}"):
            registro_h = {"equipamento": p.get('equipamento'), "periodo": p.get('periodo'), "data_prevista": p.get('data_prevista'), "data_conclusao": datetime.now().strftime("%d/%m/%Y %H:%M"), "pecas": p.get('pecas'), "status": "Concluído"}
            st.session_state.historico_local.append(registro_h)
            if not MODO_DEMO:
                try:
                    requests.post(f"{SUB_URL}/rest/v1/historico", json=registro_h, headers=SUB_HEADERS, timeout=5)
                    requests.delete(f"{SUB_URL}/rest/v1/planejamento?id=eq.{p.get('id')}", headers=SUB_HEADERS, timeout=5)
                except: pass
            st.session_state.planejamento_local = [item for item in st.session_state.planejamento_local if item.get('id') != p.get('id')]
            st.success("Ordem finalizada!")
            st.rerun()
        st.write("---")

elif menu == "📜 Histórico de Trocas":
    st.header("📜 Histórico de Serviços Concluídos")
    st.subheader("📊 Gráfico de Evolução dos Serviços por Período")
    p_semanal = sum(1 for x in todos_agendamentos if str(x.get('periodo')).lower() == 'semanal')
