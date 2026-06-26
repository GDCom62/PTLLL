import streamlit as st
from datetime import datetime
import base64
import os
import requests

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Controle de Manutenção & PT", layout="wide", page_icon="⚙️")

def main():
    # Inicializa variáveis de controle de fluxo de dados
    MODO_DEMO = False
    SUB_URL = ""
    SUB_HEADERS = {}

    # --- CAMADA DE PROTEÇÃO CONTRA TELA EM BRANCO (SECRETS) ---
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

    # Inicializa a memória volátil de segurança do Streamlit para evitar travar as listas
    if "maquinas_locais" not in st.session_state:
        st.session_state.maquinas_locais = [
            {"id": "EQ-001", "nome": "Torno Mecânico Nardini", "localizacao": "Oficina Central", "criticidade": "Alta", "check_semanal": "Óleo e limpeza", "check_mensal": "Filtros", "check_anual": "Motor"},
            {"id": "EQ-002", "nome": "Compressor de Ar Schulz", "localizacao": "Sala de Compressores", "criticidade": "Média", "check_semanal": "Drenar", "check_mensal": "Filtro", "check_anual": "Válvulas"}
        ]
    if "planejamento_local" not in st.session_state:
        st.session_state.planejamento_local = []
    if "historico_local" not in st.session_state:
        st.session_state.historico_local = []

    # Se estiver conectado ao Supabase, tenta alimentar os dados iniciais na nuvem
    if not MODO_DEMO:
        try:
            req_check = requests.get(SUB_URL + "/rest/v1/equipamentos?select=id", headers=SUB_HEADERS, timeout=5)
            if req_check.status_code == 200 and len(req_check.json()) == 0:
                for mq in st.session_state.maquinas_locais:
                    requests.post(SUB_URL + "/rest/v1/equipamentos", json=mq, headers=SUB_HEADERS, timeout=5)
        except:
            MODO_DEMO = True # Se a internet ou o link falhar, cai no modo demo seguro

    # --- FUNÇÃO AUXILIAR PARA CORREÇÃO DE LOGO NA NUVEM ---
    def carregar_imagem_base64(caminho_imagem):
        if os.path.exists(caminho_imagem):
            with open(caminho_imagem, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode()
        return None

    # --- ADIÇÃO DOS LOGOS ---
    if os.path.exists("logo.png"):
        st.image("logo.png", width=150)
    else:
        st.info("Insira o arquivo 'logo.png' na pasta do script para exibir o logo do topo.")

    logo1_b64 = carregar_imagem_base64("logo1.png")
    if logo1_b64:
        st.markdown(
            f"""
            <style>
            .developer-logo {{ position: fixed; bottom: 10px; right: 10px; width: 60px; z-index: 9999; opacity: 0.7; transition: opacity 0.3s; }}
            .developer-logo:hover {{ opacity: 1.0; }}
            </style>
            <img src="data:image/png;base64,{logo1_b64}" class="developer-logo">
            """,
            unsafe_html=True
        )

    # Alerta visual caso o banco em nuvem apresente alguma instabilidade
    if MODO_DEMO:
        st.warning("⚠️ Sistema operando em Modo Local temporário. Verifique os Secrets do Supabase no painel do Streamlit.")

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
        
        # Puxa os dados da Nuvem ou da memória Local
        equipamentos = []
        if not MODO_DEMO:
            try:
                req = requests.get(SUB_URL + "/rest/v1/equipamentos?select=*&order=id.asc", headers=SUB_HEADERS, timeout=5)
                equipamentos = req.json() if req.status_code == 200 else st.session_state.maquinas_locais
            except:
                equipamentos = st.session_state.maquinas_locais
        else:
            equipamentos = st.session_state.maquinas_locais

        with aba_lista:
            st.subheader("Equipamentos Registrados no Sistema")
            if len(equipamentos) > 0 and isinstance(equipamentos, list):
                for eq in equipamentos:
                    st.write(f"🔹 **[{eq['id']}] {eq['nome']}** | Setor: {eq['localizacao']} | Criticidade: {eq['criticidade']}")
                    if st.button("🗑️ Remover " + str(eq['id']), key="del_" + str(eq['id'])):
                        if not MODO_DEMO:
                            try: requests.delete(SUB_URL + "/rest/v1/equipamentos?id=eq." + str(eq['id']), headers=SUB_HEADERS, timeout=5)
                            except: pass
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
                            "check_semanal": c_sem, "check_mensal": c_mes, "check_anual": c_ano
                        }
                        if not MODO_DEMO:
                            try: requests.post(SUB_URL + "/rest/v1/equipamentos", json=novo_registro, headers=SUB_HEADERS, timeout=5)
                            except: pass
                        st.session_state.maquinas_locais.append(novo_registro)
                        st.success("Máquina registrada com sucesso!")
                        st.rerun()
                    else:
                        st.error("Preencha os campos obrigatórios.")

        with aba_editar:
            st.subheader("Editar Máquina Existente")
            opcoes_edicao = {e['id'] + " - " + e['nome']: e for e in equipamentos} if isinstance(equipamentos, list) else {}
            
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
                        if not MODO_DEMO:
                            try: requests.patch(SUB_URL + "/rest/v1/equipamentos?id=eq." + str(eq_para_editar['id']), json=alteracoes, headers=SUB_HEADERS, timeout=5)
                            except: pass
                        for m in st.session_state.maquinas_locais:
                            if m['id'] == eq_para_editar['id']:
                                m.update(alteracoes)
                        st.success("Alterações salvas!")
                        st.rerun()

    # ==========================================
    # 2. PÁGINA: PLANEJAMENTO TEMPORAL
    # ==========================================
    elif menu == "📅 Planejamento & Checklists":
        st.header("📅 Planejamento de Manutenções Preventivas")
