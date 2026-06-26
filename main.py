import streamlit as st
from datetime import datetime
import base64
import os
import requests

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Controle de Manutenção & PT", layout="wide", page_icon="⚙️")

# --- CONEXÃO COM O BANCO DE DADOS EM NUVEM SUPABASE VIA API HTTP NATIVA ---
@st.cache_resource
def obter_credenciais_supabase():
    """Busca as credenciais com segurança, limpa e padroniza a URL da API"""
    url_base = st.secrets["SUPABASE_URL"].strip().rstrip("/")
    if "/rest/v1" in url_base:
        url_base = url_base.split("/rest/v1")[0]
        
    key = st.secrets["SUPABASE_KEY"].strip()
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    return url_base, headers

try:
    SUB_URL, SUB_HEADERS = obter_credenciais_supabase()
except Exception as e:
    st.error("Erro ao ler credenciais. Verifique os Secrets do Streamlit.")
    st.stop()

# --- VERIFICAÇÃO E ALIMENTAÇÃO AUTOMÁTICA DA NUVEM ---
try:
    req_check = requests.get(f"{SUB_URL}/rest/v1/equipamentos?select=id", headers=SUB_HEADERS)
    if req_check.status_code == 200 and len(req_check.json()) == 0:
        maquinas_iniciais = [
            {"id": "EQ-001", "nome": "Torno Mecânico Nardini", "localizacao": "Oficina Central", "criticidade": "Alta", "check_semanal": "Óleo e limpeza", "check_mensal": "Filtros", "check_anual": "Motor"},
            {"id": "EQ-002", "nome": "Compressor de Ar Schulz", "localizacao": "Sala de Compressores", "criticidade": "Média", "check_semanal": "Drenar", "check_mensal": "Filtro", "check_anual": "Válvulas"}
        ]
        for mq in maquinas_iniciais:
            requests.post(f"{SUB_URL}/rest/v1/equipamentos", json=mq, headers=SUB_HEADERS)
except:
    pass

# --- FUNÇÃO AUXILIAR PARA CORREÇÃO DE LOGO NA NUVEM ---
def carregar_imagem_base64(caminho_imagem):
    if os.path.exists(caminho_imagem):
        with open(caminho_imagem, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    return None

# --- ADIÇÃO DOS LOGOS (LOGO REDUZIDO PELA METADE) ---
if os.path.exists("logo.png"):
    st.image("logo.png", width=150)
else:
    st.info("Insira o arquivo 'logo.png' na pasta do script para exibir o logo do topo.")

logo1_b64 = carregar_imagem_base64("logo1.png")
if logo1_b64:
    st.markdown(
        f"""
        <style>
        .developer-logo {{
            position: fixed;
            bottom: 10px;
            right: 10px;
            width: 60px;
            z-index: 9999;
            opacity: 0.7;
            transition: opacity 0.3s;
        }}
        .developer-logo:hover {{
            opacity: 1.0;
        }}
        </style>
        <img src="data:image/png;base64,{logo1_b64}" class="developer-logo">
        """,
        unsafe_html=True
    )

# --- MARCA DA EMPRESA NO MENU LATERAL ---
st.sidebar.markdown("**Desenvolvido por GDCOM**")
st.sidebar.title("⚙️ Gestão de Manutenção")
menu = st.sidebar.radio("Navegar para:", [
    "📋 Cadastro & Edição de Máquinas", 
    "📅 Planejamento & Checklists", 
    "📜 Histórico de Trocas", 
    "⚠️ Emissão de PT"
])

# ==========================================
# 1. PÁGINA: CADASTRO E EDIÇÃO
# ==========================================
if menu == "📋 Cadastro & Edição de Máquinas":
    st.header("📋 Gerenciamento de Máquinas e Equipamentos")
    aba_lista, aba_cadastrar, aba_editar = st.tabs(["🔍 Ver e Excluir", "➕ Cadastrar Novo", "✏️ Editar Existente"])
    
    with aba_lista:
        st.subheader("Equipamentos Registrados no Sistema")
        req = requests.get(f"{SUB_URL}/rest/v1/equipamentos?select=*&order=id.asc", headers=SUB_HEADERS)
        equipamentos = req.json() if req.status_code == 200 else []
        
        if len(equipamentos) > 0 and isinstance(equipamentos, list):
            for eq in equipamentos:
                st.write(f"🔹 **[{eq['id']}] {eq['nome']}** | Setor: {eq['localizacao']} | Criticidade: {eq['criticidade']}")
                if st.button("🗑️ Remover " + str(eq['id']), key="del_" + str(eq['id'])):
                    requests.delete(f"{SUB_URL}/rest/v1/equipamentos?id=eq.{eq['id']}", headers=SUB_HEADERS)
                    st.success("Equipamento removido do banco de dados na nuvem!")
                    st.rerun()
                st.write("---")
        else:
            st.info("Nenhum equipamento cadastrado no sistema.")
                        
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
                    novo_registro = {
                        "id": id_eq, "nome": nome_eq, "localizacao": local_eq, "criticidade": crit_eq,
                        "check_semanal": c_sem, "check_mensal": c_mes, "check_anual": c_ano
                    }
                    res = requests.post(f"{SUB_URL}/rest/v1/equipamentos", json=novo_registro, headers=SUB_HEADERS)
                    if res.status_code < 400:
                        st.success("Máquina registrada e salva permanentemente na nuvem!")
                        st.rerun()
                    else:
                        st.error(f"Erro ao salvar no banco em nuvem: {res.text}")
                else:
                    st.error("Preencha os campos obrigatórios.")

    with aba_editar:
        st.subheader("Editar Máquina Existente")
        req = requests.get(f"{SUB_URL}/rest/v1/equipamentos?select=*", headers=SUB_HEADERS)
        equipamentos_lista = req.json() if req.status_code == 200 else []
        opcoes_edicao = {}
        if isinstance(equipamentos_lista, list):
            opcoes_edicao = {e['id'] + " - " + e['nome']: e for e in equipamentos_lista}
        
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
                    alteracoes = {
                        "nome": novo_nome, "localizacao": novo_local, "criticidade": novo_crit,
                        "check_semanal": n_sem, "check_mensal": n_mes, "check_anual": n_ano
                    }
                    requests.patch(f"{SUB_URL}/rest/v1/equipamentos?id=eq.{eq_para_editar['id']}", json=alteracoes, headers=SUB_HEADERS)
                    st.success("Alterações salvas com sucesso na nuvem!")
                    st.rerun()

# ==========================================
# 2. PÁGINA: PLANEJAMENTO TEMPORAL
# ==========================================
elif menu == "📅 Planejamento & Checklists":
    st.header("📅 Planejamento de Manutenções Preventivas")
    aba_sem, aba_mes, aba_ano, aba_novo = st.tabs(["🗓️ Semanal", "📅 Mensal", "⏳ Anual", "➕ Agendar Preventiva"])
    
    req_plan = requests.get(f"{SUB_URL}/rest/v1/planejamento?status=eq.Pendente&select=*&order=id.asc", headers=SUB_HEADERS)
    todos_agendamentos = req_plan.json() if req_plan.status_code == 200 else []

    def renderizar_lista_preventivas(dados_filtrados):
        if dados_filtrados and isinstance(dados_filtrados, list):
            for p in dados_filtrados:
                col_dados, col_acao = st.columns()
                with col_dados:
                    st.write(f"⚙️ **{p['equipamento']}** | 📅 **Data Prevista:** {p.get('data_prevista')} | **Status:** {p['status']}")
                    st.write(f"🔧 Peças Programadas: {p['pecas']}")
                with col_acao:
                    if st.button("✔️ Concluir", key="comp_" + str(p['id'])):
                        registro_historico = {
                            "equipamento": p['equipamento'],
                            "periodo": p['periodo'],
                            "data_prevista": p['data_prevista'],
                            "data_conclusao": datetime.now().strftime("%d/%m/%Y %H:%M"),
                            "pecas": p['pecas'],
                            "status": "Concluído"
                        }
                        requests.post(f"{SUB_URL}/rest/v1/historico", json=registro_historico, headers=SUB_HEADERS)
                        requests.delete(f"{SUB_URL}/rest/v1/planejamento?id=eq.{p['id']}", headers=SUB_HEADERS)
                        st.success("Ordem de serviço finalizada!")
                        st.rerun()
                st.write("---")
        else:
            st.info("Nenhuma manutenção preventiva pendente para este período.")

    with aba_sem:
