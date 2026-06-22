import streamlit as st
from datetime import datetime
import base64
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Controle de Manutenção & PT", layout="wide", page_icon="⚙️")

# --- FUNÇÃO AUXILIAR PARA CORREÇÃO DE LOGO NA NUVEM ---
def carregar_imagem_base64(caminho_imagem):
    if os.path.exists(caminho_imagem):
        with open(caminho_imagem, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    return None

# --- ADIÇÃO DOS LOGOS ---
if os.path.exists("logo.png"):
    st.image("logo.png", width=300)
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

# --- BANCO DE DADOS FIXO INDUSTRIAL ---
MÁQUINAS_PADRÃO = [
    {
        "id": "EQ-001", 
        "nome": "Torno Mecânico Nardini", 
        "localizacao": "Oficina Central", 
        "criticidade": "Alta",
        "check_semanal": "Verificar nível de óleo e lubrificação geral\nLimpeza de resíduos e cavacos\nTestar botão de emergência",
        "check_mensal": "Trocar filtros de óleo\nVerificar tensão de correias",
        "check_anual": "Revisão do motor elétrico\nSubstituição do fluido hidráulico"
    },
    {
        "id": "EQ-002", 
        "nome": "Compressor de Ar Schulz", 
        "localizacao": "Sala de Compressores", 
        "criticidade": "Média",
        "check_semanal": "Drenar condensado do reservatório\nVerificar ruídos anormais",
        "check_mensal": "Limpar filtro de ar\nVerificar nível de óleo",
        "check_anual": "Teste hidrostático do vaso\nTroca de válvulas de segurança"
    }
]

# Inicialização segura na memória operacional
if "equipamentos" not in st.session_state:
    st.session_state.equipamentos = MÁQUINAS_PADRÃO.copy()

if "planejamento" not in st.session_state:
    st.session_state.planejamento = [
        {
            "id": 1,
            "equipamento": "Torno Mecânico Nardini",
            "periodo": "Semanal",
            "data_prevista": datetime.now().strftime("%d/%m/%Y"),
            "pecas": "Inspeção preventiva padrão",
            "status": "Pendente",
            "seguranca": "Uso de EPIs obrigatório. Lockout/Tagout."
        }
    ]

if "historico" not in st.session_state:
    st.session_state.historico = []

# --- FUNÇÕES DE COMANDO (CALLBACKS) PARA SALVAMENTO DIRETO ---
def realizar_cadastro():
    id_eq = st.session_state.get("cad_id", "").strip()
    nome_eq = st.session_state.get("cad_nome", "").strip()
    if not id_eq or not nome_eq:
        st.error("Preencha o Código e o Nome do Equipamento.")
        return
    if any(e['id'] == id_eq for e in st.session_state.equipamentos):
        st.error("Este Código/Tag já está cadastrado!")
        return
    st.session_state.equipamentos.append({
        "id": id_eq,
        "nome": nome_eq,
        "localizacao": st.session_state.get("cad_local", ""),
        "criticidade": st.session_state.get("cad_crit", "Média"),
        "check_semanal": st.session_state.get("cad_sem", ""),
        "check_mensal": st.session_state.get("cad_mes", ""),
        "check_anual": st.session_state.get("cad_ano", "")
    })
    st.toast("Máquina registrada com sucesso!")

def realizar_edicao(id_alvo):
    for e in st.session_state.equipamentos:
        if e['id'] == id_alvo:
            e['nome'] = st.session_state.get("edit_nome", e['nome'])
            e['localizacao'] = st.session_state.get("edit_local", e['localizacao'])
            e['criticidade'] = st.session_state.get("edit_crit", e['criticidade'])
            e['check_semanal'] = st.session_state.get("edit_sem", e.get('check_semanal', ''))
            e['check_mensal'] = st.session_state.get("edit_mes", e.get('check_mensal', ''))
            e['check_anual'] = st.session_state.get("edit_ano", e.get('check_anual', ''))
    st.toast("Alterações salvas com sucesso!")

def realizar_agendamento():
    if st.session_state.get("plan_eq") == "Nenhum equipamento cadastrado":
        st.error("Por favor, cadastre uma máquina antes de agendar.")
        return
    novo_id = len(st.session_state.planejamento) + 1
    st.session_state.planejamento.append({
        "id": novo_id,
        "equipamento": st.session_state.get("plan_eq"),
        "periodo": st.session_state.get("plan_per"),
        "data_prevista": st.session_state.get("plan_data").strftime("%d/%m/%Y"),
        "pecas": st.session_state.get("plan_pecas"),
        "status": "Pendente",
        "seguranca": "Uso de EPIs obrigatório."
    })
    if "pt_gerada_html" in st.session_state:
        st.session_state.pt_gerada_html = None
    st.toast("Manutenção agendada com sucesso!")

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
        if st.session_state.equipamentos:
            for eq in list(st.session_state.equipamentos):
                st.write(f"🔹 **[{eq['id']}] {eq['nome']}** | Setor: {eq['localizacao']} | Criticidade: {eq['criticidade']}")
                if st.button("🗑️ Remover " + str(eq['id']), key="del_" + str(eq['id'])):
                    st.session_state.equipamentos = [e for e in st.session_state.equipamentos if e['id'] != eq['id']]
                    st.success("Equipamento removido!")
                    st.rerun()
                st.write("---")
        else:
            st.info("Nenhum equipamento cadastrado no sistema.")
                        
    with aba_cadastrar:
        st.subheader("Cadastrar Nova Máquina")
        st.text_input("Código/Tag do Equipamento (Ex: EQ-003):", key="cad_id")
        st.text_input("Nome do Equipamento:", key="cad_nome")
        st.text_input("Localização / Setor:", key="cad_local")
        st.selectbox("Criticidade:", ["Baixa", "Média", "Alta"], key="cad_crit", index=1)
        st.markdown("---")
        st.text_area("Itens da Preventiva Semanal:", "Verificar nível de óleo\nLimpeza geral", key="cad_sem")
        st.text_area("Itens da Preventiva Mensal:", "Trocar filtros\nConferir correias", key="cad_mes")
        st.text_area("Itens da Preventiva Anual:", "Revisão geral do motor", key="cad_ano")
        st.button("💾 Salvar Equipamento", type="primary", on_click=realizar_cadastro)

    with aba_editar:
        st.subheader("Editar Máquina Existente")
        opcoes_edicao = {e['id'] + " - " + e['nome']: e for e in st.session_state.equipamentos}
        if opcoes_edicao:
            selecionado_edicao = st.selectbox("Selecione qual máquina deseja alterar:", list(opcoes_edicao.keys()))
            eq_para_editar = opcoes_edicao[selecionado_edicao]
            
            st.text_input("Nome do Equipamento:", value=eq_para_editar['nome'], key="edit_nome")
            st.text_input("Localização / Setor:", value=eq_para_editar['localizacao'], key="edit_local")
            st.selectbox("Criticidade:", ["Baixa", "Média", "Alta"], index=["Baixa", "Média", "Alta"].index(eq_para_editar['criticidade']), key="edit_crit")
            st.text_area("Preventiva Semanal:", value=eq_para_editar.get('check_semanal', ''), key="edit_sem")
            st.text_area("Preventiva Mensal:", value=eq_para_editar.get('check_mensal', ''), key="edit_mes")
            st.text_area("Preventiva Anual:", value=eq_para_editar.get('check_anual', ''), key="edit_ano")
            st.button("📝 Gravar Alterações", type="primary", on_click=realizar_edicao, args=(eq_para_editar['id'],))
        else:
            st.info("Nenhum equipamento cadastrado para edição.")

# ==========================================
# 2. PÁGINA: PLANEJAMENTO TEMPORAL
# ==========================================
elif menu == "📅 Planejamento & Checklists":
    st.header("📅 Planejamento de Manutenções Preventivas")
    aba_sem, aba_mes, aba_ano, aba_novo = st.tabs(["🗓️ Semanal", "📅 Mensal", "⏳ Anual", "➕ Agendar Preventiva"])
    
    with aba_sem:
        dados_sem = [p for p in st.session_state.planejamento if p['periodo'] == "Semanal" and p['status'] == "Pendente"]
        for p in dados_sem:
            st.write("⚙️ **" + str(p['equipamento']) + "** | 📅 **Data:** " + str(p.get('data_prevista')) + " | **Status:** " + str(p['status']))
            st.write("🔧 Peças Programadas: " + str(p['pecas']))
            st.write("---")

    with aba_mes:
        dados_mes = [p for p in st.session_state.planejamento if p['periodo'] == "Mensal" and p['status'] == "Pendente"]
        for p in dados_mes:
            st.write("⚙️ **" + str(p['equipamento']) + "** | 📅 **Data:** " + str(p.get('data_prevista')) + " | **Status:** " + str(p['status']))
            st.write("🔧 Peças Programadas: " + str(p['pecas']))
            st.write("---")

    with aba_ano:
        dados_ano = [p for p in st.session_state.planejamento if p['periodo'] == "Anual" and p['status'] == "Pendente"]
        for p in dados_ano:
