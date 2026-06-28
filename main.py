import streamlit as st
from datetime import datetime
import os
import requests

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Controle de Manutenção & PT", layout="wide", page_icon="⚙️")

# --- CONEXÃO AVANÇADA COM DIAGNÓSTICO SUPABASE ---
SUB_URL = ""
SUB_HEADERS = {}
MODO_DEMO = False
STATUS_CONEXAO = "Não configurado"

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
        STATUS_CONEXAO = "Chaves carregadas. Prontos para testar rotas."
    else:
        MODO_DEMO = True
        STATUS_CONEXAO = "Secrets 'SUPABASE_URL' ou 'SUPABASE_KEY' ausentes."
except Exception as e:
    MODO_DEMO = True
    STATUS_CONEXAO = f"Erro crítico ao ler Secrets: {e}"

# --- MOTOR DE FORÇAMENTO DE MEMÓRIA (LIMPA O CACHE TRAVADO DO STREAMLIT) ---
# Se as variáveis locais sumiram ou viraram listas vazias, este bloco reconstrói do zero
if "maquinas_locais" not in st.session_state or not st.session_state.maquinas_locais:
    st.session_state.maquinas_locais = [
        {"id": "EQ-001", "nome": "Torno Mecânico Nardini", "localizacao": "Oficina Central", "criticidade": "Alta", "check_semanal": "Óleo e limpeza", "check_mensal": "Filtros", "check_anual": "Motor"},
        {"id": "EQ-002", "nome": "Compressor de Ar Schulz", "localizacao": "Sala de Compressores", "criticidade": "Média", "check_semanal": "Drenar", "check_mensal": "Filtro", "check_anual": "Válvulas"}
    ]

if "planejamento_local" not in st.session_state or not st.session_state.planejamento_local:
    st.session_state.planejamento_local = [
        {"id": 1, "equipamento": "Torno Mecânico Nardini", "periodo": "Semanal", "data_prevista": datetime.now().strftime("%d/%m/%Y"), "pecas": "Inspeção preventiva padrão e lubrificação", "status": "Pendente"}
    ]

if "historico_local" not in st.session_state:
    st.session_state.historico_local = []

# --- MARCA DA EMPRESA NO MENU LATERAL ---
st.sidebar.markdown("**Desenvolvido por GDCOM**")
st.sidebar.title("⚙️ Gestão de Manutenção")

menu = st.sidebar.radio("Navegar para:", [
    "🔍 Lista de Máquinas",
    "➕ Cadastrar Nova Máquina",
    "✏️ Editar Máquina",
    "📅 Planejamento & Checklists",
    "📜 Histórico de Trocas",
    "⚠️ Emissão de PT",
    "🛠️ Diagnóstico de Conexão"
])

# --- CARREGAMENTO INTEGRADO DE EQUIPAMENTOS ---
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

# --- CARREGAMENTO INTEGRADO DE AGENDAMENTOS ---
todos_agendamentos = []
if not MODO_DEMO:
    try:
        req_plan = requests.get(f"{SUB_URL}/rest/v1/planejamento?status=eq.Pendente", headers=SUB_HEADERS, timeout=5)
        if req_plan.status_code == 200 and isinstance(req_plan.json(), list):
            todos_agendamentos = req_plan.json()
    except:
        pass

# Casamento forçado de segurança: se a nuvem não trouxe listas válidas, injeta o backup local
if not todos_agendamentos or len(todos_agendamentos) == 0:
    todos_agendamentos = list(st.session_state.planejamento_local)

# ==========================================
# PAGE: DIAGNÓSTICO DE CONEXÃO
# ==========================================
if menu == "🛠️ Diagnóstico de Conexão":
    st.header("🛠️ Painel Analítico de Conexão com o Supabase")
    st.code(f"URL Alvo: {SUB_URL}\nModo Local Ativo: {MODO_DEMO}\nDiagnóstico: {STATUS_CONEXAO}")
    
    if st.button("⚡ Executar Teste de Gravação Forçado"):
        id_dinamica = "TST-" + datetime.now().strftime("%M%S")
        try:
            teste_payload = {"id": id_dinamica, "nome": "Equipamento Teste Dinâmico", "localizacao": "Laboratório", "criticidade": "Baixa"}
            res = requests.post(f"{SUB_URL}/rest/v1/equipamentos", json=teste_payload, headers=SUB_HEADERS, timeout=5)
            if res.status_code == 201 or res.status_code == 200:
                st.success("🎉 Conexão ativa!")
                requests.delete(f"{SUB_URL}/rest/v1/equipamentos?id=eq.{id_dinamica}", headers=SUB_HEADERS, timeout=5)
            else:
                st.error(f"Erro: {res.status_code} - {res.text}")
        except Exception as e:
            st.error(f"Erro: {e}")

# ==========================================
# PAGE 1: LISTA DE MÁQUINAS
# ==========================================
elif menu == "🔍 Lista de Máquinas":
    st.header("🔍 Equipamentos Registrados no Sistema")
    if equipamentos:
        for idx, eq in enumerate(equipamentos):
            eq_id = eq.get('id', eq.get('tag', f"REG-{idx}"))
            eq_nome = eq.get('nome', eq.get('equipamento', 'Sem Nome'))
            eq_local = eq.get('localizacao', eq.get('setor', 'Não Definido'))
            eq_crit = eq.get('criticidade', 'Média')
            
            st.write(f"🔹 **[{eq_id}] {eq_nome}** | Setor: {eq_local} | Criticidade: {eq_crit}")
            if st.button("🗑️ Remover " + str(eq_id), key="del_" + str(eq_id) + "_" + str(idx)):
                if not MODO_DEMO:
                    try: requests.delete(f"{SUB_URL}/rest/v1/equipamentos?id=eq.{eq_id}", headers=SUB_HEADERS, timeout=5)
                    except: pass
                st.session_state.maquinas_locais = [m for m in st.session_state.maquinas_locais if m.get('id') != eq_id]
                st.success("Equipamento removido!")
                st.rerun()
            st.write("---")

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
        botao_salvar = st.form_submit_button("Salvar Equipamento")
        
    if botao_salvar:
        if id_eq and nome_eq:
            payload_completo = {"id": id_eq, "nome": nome_eq, "localizacao": local_eq, "criticidade": crit_eq, "check_semanal": c_sem, "check_mes": c_mes, "check_anual": c_ano}
            payload_simplificado = {"id": id_eq, "nome": nome_eq, "localizacao": local_eq, "criticidade": crit_eq}
            
            if payload_completo not in st.session_state.maquinas_locais:
                st.session_state.maquinas_locais.append(payload_completo)
            
            if not MODO_DEMO:
                try:
                    headers_gravacao = SUB_HEADERS.copy()
                    headers_gravacao["Prefer"] = "resolution=merge-duplicates"
                    res = requests.post(f"{SUB_URL}/rest/v1/equipamentos", json=payload_completo, headers=headers_gravacao, timeout=10)
                    if res.status_code != 201 and res.status_code == 400:
                        requests.post(f"{SUB_URL}/rest/v1/equipamentos", json=payload_simplificado, headers=headers_gravacao, timeout=10)
                    st.success("🎉 Gravado com sucesso no Supabase!")
                except:
                    pass
            st.rerun()
        else:
            st.error("Preencha os campos obrigatórios.")

# ==========================================
# PAGE 3: EDITAR MÁQUINA
# ==========================================
elif menu == "✏️ Editar Máquina":
    st.header("✏️ Editar Máquina Existente")
    opcoes_edicao = {f"{e.get('id', idx)} - {e.get('nome', 'Equipamento')}": e for idx, e in enumerate(equipamentos)}
    if opcoes_edicao:
        selecionado_edicao = st.selectbox("Selecione qual máquina deseja alterar:", list(opcoes_edicao.keys()))
        eq_para_editar = opcoes_edicao[selecionado_edicao]
        
        with st.form("form_edicao"):
            novo_nome = st.text_input("Nome:", value=eq_para_editar.get('nome', eq_para_editar.get('equipamento', '')))
            novo_local = st.text_input("Setor:", value=eq_para_editar.get('localizacao', eq_para_editar.get('setor', '')))
            novo_crit = st.selectbox("Criticidade:", ["Baixa", "Média", "Alta"], index=["Baixa", "Média", "Alta"].index(eq_para_editar.get('criticidade', 'Média')))
            n_sem = st.text_area("Semanal:", value=eq_para_editar.get('check_semanal', ''))
            n_mes = st.text_area("Mensal:", value=eq_para_editar.get('check_mes', ''))
            n_ano = st.text_area("Anual:", value=eq_para_editar.get('check_anual', ''))
            botao_editar = st.form_submit_button("Gravar Alterações")
            
        if botao_editar:
            alteracoes = {"nome": novo_nome, "localizacao": novo_local, "criticidade": novo_crit, "check_semanal": n_sem, "check_mes": n_mes, "check_anual": n_ano}
            if not MODO_DEMO:
                try:
                    eq_id_alvo = eq_para_editar.get('id', eq_para_editar.get('tag', '0'))
                    requests.patch(f"{SUB_URL}/rest/v1/equipamentos?id=eq.{eq_id_alvo}", json=alteracoes, headers=SUB_HEADERS, timeout=5)
                except: pass
            st.success("Alterações salvas!")
            st.rerun()
    else:
