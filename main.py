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
        # Garante a limpeza correta da URL e chaves eliminando barras extras
        SUB_URL = str(st.secrets["SUPABASE_URL"]).strip().rstrip("/")
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

# --- INICIALIZAÇÃO DA MEMÓRIA DE SEGURANÇA LOCAL ---
if "maquinas_locais" not in st.session_state:
    st.session_state.maquinas_locais = [
        {"id": "EQ-001", "nome": "Torno Mecânico Nardini", "localizacao": "Oficina Central", "criticidade": "Alta", "check_semanal": "Óleo e limpeza", "check_mensal": "Filtros", "check_anual": "Motor"},
        {"id": "EQ-002", "nome": "Compressor de Ar Schulz", "localizacao": "Sala de Compressores", "criticidade": "Média", "check_semanal": "Drenar", "check_mensal": "Filtro", "check_anual": "Válvulas"}
    ]

if "planejamento_local" not in st.session_state:
    st.session_state.planejamento_local = [
        {"id": 1, "equipamento": "Torno Mecânico Nardini", "periodo": "Semanal", "data_prevista": datetime.now().strftime("%d/%m/%Y"), "pecas": "Inspeção preventiva padrão e lubrificação", "status": "Pendente", "seguranca": "Uso de EPIs obrigatório."}
    ]

if "historico_local" not in st.session_state:
    st.session_state.historico_local = []

# --- INJEÇÃO DE DADOS SE O BANCO DA NUVEM ESTIVER VAZIO ---
if not MODO_DEMO:
    try:
        rota_check = SUB_URL + "/rest/v1/equipamentos?select=id"
        req_check = requests.get(rota_check, headers=SUB_HEADERS, timeout=5)
        if req_check.status_code == 200 and len(req_check.json()) == 0:
            rota_insert = SUB_URL + "/rest/v1/equipamentos"
            for mq in st.session_state.maquinas_locais:
                requests.post(rota_insert, json=mq, headers=SUB_HEADERS, timeout=5)
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
        rota_get = SUB_URL + "/rest/v1/equipamentos?select=*&order=id.asc"
        req = requests.get(rota_get, headers=SUB_HEADERS, timeout=5)
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
                        rota_del = SUB_URL + "/rest/v1/equipamentos?id=eq." + str(eq['id'])
                        res_del = requests.delete(rota_del, headers=SUB_HEADERS, timeout=5)
                        if res_del.status_code not in:
                            st.error(f"Erro ao deletar no Supabase: Código {res_del.status_code}")
                    except Exception as err:
                        st.error(f"Erro de rede Supabase: {err}")
                
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
                        rota_post = SUB_URL + "/rest/v1/equipamentos"
                        res_post = requests.post(rota_post, json=novo_registro, headers=SUB_HEADERS, timeout=15)
                        if res_post.status_code not in:
                            st.error(f"Supabase recusou o salvamento: Código {res_post.status_code}.")
                    except Exception as err:
                        st.error(f"Falha de conexão com o banco em nuvem: {err}")
                
                st.success("Máquina registrada com sucesso!")
                st.rerun()
            else:
                st.error("Preencha os campos obrigatórios.")

# ==========================================
# PAGE 3: EDITAR MÁQUINA
# ==========================================
elif menu == "✏️ Editar Máquina":
    st.header("✏️ Editar Máquina Existente")
    opcoes_edicao = {str(e['id']) + " - " + str(e['nome']): e for e in equipamentos if isinstance(e, dict) and 'id' in e}
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
                        rota_patch = SUB_URL + "/rest/v1/equipamentos?id=eq." + str(eq_para_editar['id'])
                        res_patch = requests.patch(rota_patch, json=alteracoes, headers=SUB_HEADERS, timeout=15)
                        if res_patch.status_code not in:
                            st.error(f"Erro de atualização na nuvem: {res_patch.status_code}")
                    except Exception as err:
                        st.error(f"Erro de rede: {err}")
                        
                for m in st.session_state.maquinas_locais:
                    if m['id'] == eq_para_editar['id']: m.update(alteracoes)
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
            rota_plan = SUB_URL + "/rest/v1/planejamento?status=eq.Pendente&select=*&order=id.asc"
            req_plan = requests.get(rota_plan, headers=SUB_HEADERS, timeout=5)
            if req_plan.status_code == 200:
                for d in req_plan.json():
                    if d not in todos_agendamentos: todos_agendamentos.append(d)
        except: pass

    st.subheader("📋 Nova Agenda Preventiva")
    lista_nomes = [row['nome'] for row in equipamentos if isinstance(row, dict) and 'nome' in row]
    opcoes_selecao = lista_nomes if lista_nomes else ["Nenhum equipamento cadastrado"]
    
