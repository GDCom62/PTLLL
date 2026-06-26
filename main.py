import streamlit as st
from datetime import datetime
import base64
import os
import requests

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Controle de Manutenção & PT", layout="wide", page_icon="⚙️")

# --- CONEXÃO SEGURA E DIRETA COM O SUPABASE ---
SUB_URL = ""
SUB_HEADERS = {}
MODO_DEMO = False

# Bloco try/except isolado e fechado imediatamente para evitar o SyntaxError
try:
    if "SUPABASE_URL" in st.secrets and "SUPABASE_KEY" in st.secrets:
        # Puxa o link como texto puro (string) sem divisões perigosas
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

# --- INICIALIZAÇÃO DA MEMÓRIA DE SEGURANÇA LOCAL ---
if "maquinas_locais" not in st.session_state:
    st.session_state.maquinas_locais = [
        {"id": "EQ-001", "nome": "Torno Mecânico Nardini", "localizacao": "Oficina Central", "criticidade": "Alta", "check_semanal": "Óleo e limpeza", "check_mensal": "Filtros", "check_anual": "Motor"},
        {"id": "EQ-002", "nome": "Compressor de Ar Schulz", "localizacao": "Sala de Compressores", "criticidade": "Média", "check_semanal": "Drenar", "check_mensal": "Filtro", "check_anual": "Válvulas"}
    ]
if "planejamento_local" not in st.session_state:
    st.session_state.planejamento_local = []
if "historico_local" not in st.session_state:
    st.session_state.historico_local = []

# --- FUNÇÃO AUXILIAR PARA RENDERIZAR LISTA DE PREVENTIVAS ---
def renderizar_lista_preventivas(dados_filtrados, modo_demo, sub_url, sub_headers):
    if dados_filtrados and isinstance(dados_filtrados, list):
        for p in dados_filtrados:
            col_dados, col_acao = st.columns()
            with col_dados:
                st.write("⚙️ **" + str(p['equipamento']) + "** | 📅 **Data Prevista:** " + str(p.get('data_prevista')) + " | **Status:** " + str(p['status']))
                st.write("🔧 Peças Programadas: " + str(p['pecas']))
            with col_acao:
                if st.button("✔️ Concluir", key="comp_" + str(p.get('id', p.get('equipamento')))):
                    registro_historico = {
                        "equipamento": p['equipamento'],
                        "periodo": p['periodo'],
                        "data_prevista": p['data_prevista'],
                        "data_conclusao": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "pecas": p['pecas'],
                        "status": "Concluído"
                    }
                    if not modo_demo:
                        try:
                            rota_hist_post = sub_url + "/rest/v1/historico"
                            requests.post(rota_hist_post, json=registro_historico, headers=sub_headers, timeout=15)
                            rota_plan_del = sub_url + "/rest/v1/planejamento?id=eq." + str(p['id'])
                            requests.delete(rota_plan_del, headers=sub_headers, timeout=15)
                        except:
                            pass
                    st.session_state.historico_local.append(registro_historico)
                    st.session_state.planejamento_local = [item for item in st.session_state.planejamento_local if item.get('id') != p.get('id')]
                    st.success("Ordem de serviço finalizada!")
                    st.rerun()
            st.write("---")
    else:
        st.info("Nenhuma manutenção preventiva pendente para este período.")

# --- INJEÇÃO AUTOMÁTICA DE DADOS SE O BANCO DA NUVEM ESTIVER VAZIO ---
if not MODO_DEMO:
    try:
        rota_check = SUB_URL + "/rest/v1/equipamentos?select=id"
        req_check = requests.get(rota_check, headers=SUB_HEADERS, timeout=15)
        if req_check.status_code == 200 and len(req_check.json()) == 0:
            rota_insert = SUB_URL + "/rest/v1/equipamentos"
            for mq in st.session_state.maquinas_locais:
                requests.post(rota_insert, json=mq, headers=SUB_HEADERS, timeout=15)
    except:
        MODO_DEMO = True

# --- EXIBIÇÃO DOS LOGOS NO TOPO ---
if os.path.exists("logo.png"):
    st.image("logo.png", width=150)
else:
    st.info("Insira o arquivo 'logo.png' na pasta do script para exibir o logo do topo.")

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
    
    equipamentos = []
    if not MODO_DEMO:
        try:
            rota_get = SUB_URL + "/rest/v1/equipamentos?select=*&order=id.asc"
            req = requests.get(rota_get, headers=SUB_HEADERS, timeout=15)
            equipamentos = req.json() if req.status_code == 200 else st.session_state.maquinas_locais
        except:
            equipamentos = st.session_state.maquinas_locais
    else:
        equipamentos = st.session_state.maquinas_locais

    with aba_lista:
        st.subheader("Equipamentos Registrados no Sistema")
        if len(equipamentos) > 0 and isinstance(equipamentos, list):
            for eq in equipamentos:
                st.write("🔹 **[" + str(eq['id']) + "] " + str(eq['nome']) + "** | Setor: " + str(eq['localizacao']) + " | Criticidade: " + str(eq['criticidade']))
                if st.button("🗑️ Remover " + str(eq['id']), key="del_" + str(eq['id'])):
                    if not MODO_DEMO:
                        try:
                            rota_del = SUB_URL + "/rest/v1/equipamentos?id=eq." + str(eq['id'])
                            requests.delete(rota_del, headers=SUB_HEADERS, timeout=15)
                        except:
                            pass
                    st.session_state.maquinas_locais = [m for m in st.session_state.maquinas_locais if m['id'] != eq['id']]
                    st.success("Equipamento removido!")
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
                        "check_semanal": c_sem, "check_mes": c_mes, "check_anual": c_ano
                    }
                    if not MODO_DEMO:
                        try:
                            rota_post = SUB_URL + "/rest/v1/equipamentos"
                            requests.post(rota_post, json=novo_registro, headers=SUB_HEADERS, timeout=15)
                        except:
                            pass
                    st.session_state.maquinas_locais.append(novo_registro)
                    st.success("Máquina registrada com sucesso!")
                    st.rerun()
                else:
                    st.error("Preencha os campos obrigatórios.")

    with aba_editar:
        st.subheader("Editar Máquina Existente")
        opcoes_edicao = {}
        if isinstance(equipamentos, list):
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
                    alteracoes = {
                        "nome": novo_nome, "localizacao": novo_local, "criticidade": novo_crit,
                        "check_semanal": n_sem, "check_mensal": n_mes, "check_anual": n_ano
                    }
