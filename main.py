import streamlit as st
from datetime import datetime
import requests

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
        {"id": "EQ-001", "nome": "Torno Mecânico Nardini", "localizacao": "Oficina Central", "criticidade": "Alta"},
        {"id": "EQ-002", "nome": "Compressor de Ar Schulz", "localizacao": "Sala de Compressores", "criticidade": "Média"}
    ]

if "planejamento_local" not in st.session_state or not st.session_state.planejamento_local:
    st.session_state.planejamento_local = [
        {"id": 1, "equipamento": "Torno Mecânico Nardini", "periodo": "Semanal", "data_prevista": datetime.now().strftime("%d/%m/%Y"), "pecas": "Inspeção padrão", "status": "Pendente"}
    ]

if "historico_local" not in st.session_state:
    st.session_state.historico_local = []

# --- MENU LATERAL DE NAVEGAÇÃO ---
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
if not equipamentos:
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
if not todos_agendamentos:
    todos_agendamentos = list(st.session_state.planejamento_local)

# ==========================================
# ABAS DO SISTEMA
# ==========================================
if menu == "🔍 Lista de Máquinas":
    st.header("🔍 Equipamentos Registrados")
    for idx, eq in enumerate(equipamentos):
        st.write(f"🔹 **[{eq.get('id', idx)}] {eq.get('nome', 'Equipamento')}** | Setor: {eq.get('localizacao', 'Geral')}")
        st.write("---")

elif menu == "➕ Cadastrar Nova Máquina":
    st.header("➕ Cadastrar Nova Máquina")
    with st.form("form_cadastro_direto"):
        id_eq = st.text_input("Código/Tag do Equipamento:")
        nome_eq = st.text_input("Nome do Equipamento:")
        local_eq = st.text_input("Localização / Setor:")
        crit_eq = st.selectbox("Criticidade:", ["Baixa", "Média", "Alta"])
        botao_salvar = st.form_submit_button("Salvar Equipamento")
        
    if botao_salvar and id_eq and nome_eq:
        payload = {"id": id_eq, "nome": nome_eq, "localizacao": local_eq, "criticidade": crit_eq}
        st.session_state.maquinas_locais.append(payload)
        if not MODO_DEMO:
            try:
                headers_g = SUB_HEADERS.copy()
                headers_g["Prefer"] = "resolution=merge-duplicates"
                requests.post(f"{SUB_URL}/rest/v1/equipamentos", json=payload, headers=headers_g, timeout=5)
            except:
                pass
        st.success("🎉 Equipamento salvo com sucesso!")
        st.rerun()

elif menu == "📅 Planejamento & Checklists":
    st.header("📅 Planejamento de Manutenções Preventivas")
    with st.form("form_agenda_direto"):
        lista_nomes = [row.get('nome', 'Máquina') for row in equipamentos]
        eq_escolhido = st.selectbox("Selecione a Máquina Alvo:", lista_nomes if lista_nomes else ["Nenhum cadastrado"])
        periodo_escolhido = st.selectbox("Escolha o Período:", ["Semanal", "Mensal", "Anual"])
        data_planejada = st.date_input("Selecione a Data:", datetime.now())
        pecas_necessarias = st.text_area("Descrição das Peças / Ferramentas:", value="Inspeção preventiva padrão")
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
        if st.button("✔️ Concluir OS", key=f"comp_{idx}"):
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
    st.header("📜 Histórico de Trocas Concluídas")
    historico_lista = []
    if not MODO_DEMO:
        try:
            req_hist = requests.get(f"{SUB_URL}/rest/v1/historico?select=*", headers=SUB_HEADERS, timeout=5)
            if req_hist.status_code == 200: historico_lista = req_hist.json()
        except: pass
    if not historico_lista: historico_lista = st.session_state.historico_local
    for h in historico_lista:
        st.write(f"✅ **{h.get('equipamento')}** | ⏱️ Concluído em: {h.get('data_conclusao', 'N/A')} | Intervenção: {h.get('pecas')}")

elif menu == "⚠️ Emissão de PT":
    st.header("⚠️ Permissão de Trabalho (PT)")
    if not todos_agendamentos:
        st.warning("Não existem manutenções pendentes no momento.")
    else:
        opcoes_os = {f"OS #{p.get('id', idx)} - {p.get('equipamento')}": p for idx, p in enumerate(todos_agendamentos)}
        os_selecionada = st.selectbox("Selecione a Ordem de Serviço:", list(opcoes_os.keys()))
        os_dados = opcoes_os[os_selecionada]
        
        with st.form("form_pt_direto"):
            executante = st.text_input("Técnico Executante:")
            emitente = st.text_input("Supervisor responsável:", value="Supervisor de Manutenção")
            r_altura = st.checkbox("Trabalho em Altura (NR-35)")
            r_eletrico = st.checkbox("Risco Elétrico (NR-10)")
            bt_gerar = st.form_submit_button("🚨 Gerar Documento de PT")
            
        if bt_gerar and executante:
            cod_doc = f"PT-{os_dados.get('id')}-{datetime.now().strftime('%M%S')}"
            st.markdown(f"""
            <div style="border:3px double #FF4B4B; padding:20px; background-color:#FFF5F5; font-family:monospace; color:#000000;">
                <h3 style="text-align:center; color:#FF4B4B;">⚠️ PERMISSÃO DE TRABALHO GEREADA</h3>
                <p><b>CÓDIGO:</b> {cod_doc}</p>
                <p><b>MÁQUINA:</b> {os_dados.get('equipamento')} | <b>SERVIÇO:</b> {os_dados.get('pecas')}</p>
                <p><b>EXECUTANTE:</b> {executante} | <b>SUPERVISOR:</b> {emitente}</p>
            </div>
            """, unsafe_html=True)
