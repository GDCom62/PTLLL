import streamlit as st
from datetime import datetime
import os
import requests

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Controle de Manutenção & PT", layout="wide", page_icon="⚙️")

# --- CONEXÃO COM O BANCO DE DADOS EM NUVEM SUPABASE VIA API HTTP ---
SUB_URL = ""
SUB_HEADERS = {}
MODO_DEMO = False

try:
    if "SUPABASE_URL" in st.secrets and "SUPABASE_KEY" in st.secrets:
        url_bruta = str(st.secrets["SUPABASE_URL"]).strip().rstrip("/")
        SUB_URL = url_bruta.replace("/rest/v1", "")
        key_limpa = str(st.secrets["SUPABASE_KEY"]).strip()
        SUB_HEADERS = {
            "apikey": key_limpa,
            "Authorization": "Bearer " + key_limpa,
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
    else:
        MODO_DEMO = True
except Exception as e:
    MODO_DEMO = True

# --- MEMÓRIA LOCAL DE SEGURANÇA CONTRA ERROS DE CONEXÃO ---
if "maquinas_locais" not in st.session_state:
    st.session_state.maquinas_locais = [
        {"id": "EQ-001", "nome": "Torno Mecânico Nardini", "localizacao": "Oficina Central", "criticidade": "Alta", "check_semanal": "Óleo e limpeza", "check_mensal": "Filtros", "check_anual": "Motor"},
        {"id": "EQ-002", "nome": "Compressor de Ar Schulz", "localizacao": "Sala de Compressores", "criticidade": "Média", "check_semanal": "Drenar", "check_mensal": "Filtro", "check_anual": "Válvulas"}
    ]
if "planejamento_local" not in st.session_state:
    st.session_state.planejamento_local = []
if "historico_local" not in st.session_state:
    st.session_state.historico_local = []

# --- INJEÇÃO DE DADOS SE O BANCO DA NUVEM ESTIVER VAZIO ---
if not MODO_DEMO:
    try:
        req_check = requests.get(SUB_URL + "/rest/v1/equipamentos?select=id", headers=SUB_HEADERS, timeout=15)
        if req_check.status_code == 200 and len(req_check.json()) == 0:
            for mq in st.session_state.maquinas_locais:
                requests.post(SUB_URL + "/rest/v1/equipamentos", json=mq, headers=SUB_HEADERS, timeout=15)
    except:
        MODO_DEMO = True

# --- EXIBIÇÃO DO LOGO NO TOPO ---
if os.path.exists("logo.png"):
    st.image("logo.png", width=150)
else:
    st.info("Insira o arquivo 'logo.png' na pasta do script para exibir o logo do topo.")

# --- MENU LATERAL DE NAVEGAÇÃO COMPACTO ---
st.sidebar.markdown("**Desenvolvido por GDCOM**")
st.sidebar.title("⚙️ Gestão de Manutenção")
menu = st.sidebar.radio("Navegar para:", [
    "🔍 Lista de Máquinas",
    "➕ Cadastrar Nova Máquina",
    "✏️ Editar Máquina",
    "📅 Planejamento & Checklists",
    "📜 Histórico de Trocas",
    "⚠️ Emissão de PT"
])

# --- PUXA DADOS DA NUVEM OU LOCAL ---
equipamentos = []
if not MODO_DEMO:
    try:
        req = requests.get(SUB_URL + "/rest/v1/equipamentos?select=*&order=id.asc", headers=SUB_HEADERS, timeout=15)
        if req.status_code == 200:
            equipamentos = req.json()
    except:
        pass

if not equipamentos or len(equipamentos) == 0:
    equipamentos = st.session_state.maquinas_locais

# ==========================================
# PAGE 1: LISTA DE MÁQUINAS
# ==========================================
if menu == "🔍 Lista de Máquinas":
    st.header("🔍 Equipamentos Registrados no Sistema")
    if equipamentos and isinstance(equipamentos, list):
        for idx, eq in enumerate(equipamentos):
            st.write("🔹 **[" + str(eq['id']) + "] " + str(eq['nome']) + "** | Setor: " + str(eq['localizacao']) + " | Criticidade: " + str(eq['criticidade']))
            if st.button("🗑️ Remover " + str(eq['id']), key="del_" + str(eq['id']) + "_" + str(idx)):
                if not MODO_DEMO:
                    try:
                        requests.delete(SUB_URL + "/rest/v1/equipamentos?id=eq." + str(eq['id']), headers=SUB_HEADERS, timeout=15)
                    except:
                        pass
                st.session_state.maquinas_locais = [m for m in st.session_state.maquinas_locais if m['id'] != eq['id']]
                st.success("Equipamento removido!")
                st.rerun()
            st.write("---")
    else:
        st.info("Nenhum equipamento cadastrado no sistema.")

# ==========================================
# PAGE 2: CADASTRAR MÁQUINA
# ==========================================
elif menu == "➕ Cadastrar Nova Máquina":
    st.header("➕ Cadastrar Nova Máquina")
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
                novo_registro = {"id": id_eq, "nome": nome_eq, "localizacao": local_eq, "criticidade": crit_eq, "check_semanal": c_sem, "check_mes": c_mes, "check_anual": c_ano}
                st.session_state.maquinas_locais.append(novo_registro)
                if not MODO_DEMO:
                    try:
                        requests.post(SUB_URL + "/rest/v1/equipamentos", json=novo_registro, headers=SUB_HEADERS, timeout=15)
                    except:
                        pass
                st.success("Máquina registrada com sucesso!")
                st.rerun()
            else:
                st.error("Preencha os campos obrigatórios.")

# ==========================================
# PAGE 3: EDITAR MÁQUINA
# ==========================================
elif menu == "✏️ Editar Máquina":
    st.header("✏️ Editar Máquina Existente")
    opcoes_edicao = {}
    if equipamentos and isinstance(equipamentos, list):
        for e in equipamentos:
            if isinstance(e, dict) and 'id' in e:
                opcoes_edicao[str(e['id']) + " - " + str(e['nome'])] = e
    
    if opcoes_edicao:
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
                alteracoes = {"nome": novo_nome, "localizacao": novo_local, "criticidade": novo_crit, "check_semanal": n_sem, "check_mensal": n_mes, "check_anual": n_ano}
                if not MODO_DEMO:
                    try:
                        requests.patch(SUB_URL + "/rest/v1/equipamentos?id=eq." + str(eq_para_editar['id']), json=alteracoes, headers=SUB_HEADERS, timeout=15)
                    except:
                        pass
                for m in st.session_state.maquinas_locais:
                    if m['id'] == eq_para_editar['id']:
                        m.update(alteracoes)
                st.success("Alterações salvas!")
                st.rerun()
    else:
        st.info("Nenhum equipamento disponível para edição.")

# ==========================================
# PAGE 4: PLANEJAMENTO TEMPORAL
# ==========================================
elif menu == "📅 Planejamento & Checklists":
    st.header("📅 Planejamento de Manutenções Preventivas")
    
    todos_agendamentos = list(st.session_state.planejamento_local)
    if not MODO_DEMO:
        try:
            req_plan = requests.get(SUB_URL + "/rest/v1/planejamento?status=eq.Pendente&select=*&order=id.asc", headers=SUB_HEADERS, timeout=15)
            if req_plan.status_code == 200:
                for d in req_plan.json():
                    if d not in todos_agendamentos:
                        todos_agendamentos.append(d)
        except:
            pass

    st.subheader("📋 Nova Agenda Preventiva")
    lista_nomes = [row['nome'] for row in equipamentos if isinstance(row, dict) and 'nome' in row]
    opcoes_selecao = lista_nomes if lista_nomes else ["Nenhum equipamento cadastrado"]
    
    with st.form("form_novo_planejamento_topo"):
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            eq_escolhido = st.selectbox("Selecione a Máquina Alvo:", opcoes_selecao)
        with col_f2:
            periodo_escolhido = st.selectbox("Escolha o Período:", ["Semanal", "Mensal", "Anual"])
        with col_f3:
            data_planejada = st.date_input("Selecione a Data:", datetime.now())
            
        pecas_necessarias = st.text_area("Descrição das Peças / Ferramentas necessárias:", value="Inspeção preventiva padrão")
        
        if st.form_submit_button("💾 Gravar e Agendar Manutenção"):
            if eq_escolhido != "Nenhum equipamento cadastrado":
                novo_agendamento = {
                    "id": len(todos_agendamentos) + 1,
                    "equipamento": eq_escolhido,
                    "periodo": periodo_escolhido,
                    "data_prevista": data_planejada.strftime("%d/%m/%Y"),
                    "pecas": pecas_necessarias,
                    "status": "Pendente",
                    "seguranca": "Uso de EPIs obrigatório."
                }
