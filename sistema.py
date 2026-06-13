import streamlit as st
import json
import os
import base64
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Controle de Manutenção & PT", layout="wide", page_icon="⚙️")

# --- FUNÇÃO PARA CONVERTER IMAGEM LOCAL EM BASE64 ---
def obter_base64_imagem(caminho_imagem):
    if os.path.exists(caminho_imagem):
        with open(caminho_imagem, "rb") as f:
            dados = f.read()
        return base64.b64encode(dados).decode()
    return None

# --- INJEÇÃO DA MARCA NO CANTO INFERIOR DIREITO DA TELA ---
img_marca_b64 = obter_base64_imagem("logo gdcom1.png")
if img_marca_b64:
    st.markdown(
        f"""
        <style>
        .marca-fixa {{
            position: fixed;
            bottom: 15px;
            right: 15px;
            z-index: 9999;
            opacity: 0.7;
            max-width: 120px;
            pointer-events: none;
        }}
        </style>
        <img src="data:image/png;base64,{img_marca_b64}" class="marca-fixa">
        """,
        unsafe_allow_html=True
    )

# --- ARQUIVOS DE ARMAZENAMENTO ---
ARQUIVO_EQ = "dados_equipamentos.json"
ARQUIVO_PLAN = "dados_planejamento.json"
ARQUIVO_HIST = "dados_historico.json"

# --- FUNÇÕES DE CARGA E SALVAMENTO ---
def carregar_dados(arquivo, dados_padrao):
    if os.path.exists(arquivo):
        try:
            with open(arquivo, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return dados_padrao
    return dados_padrao

def salvar_dados(arquivo, dados):
    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

# --- INICIALIZAÇÃO DOS DADOS ---
if "equipamentos" not in st.session_state:
    st.session_state.equipamentos = carregar_dados(ARQUIVO_EQ, [
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
        },
    ])

if "historico" not in st.session_state:
    st.session_state.historico = carregar_dados(ARQUIVO_HIST, [])

if "planejamento" not in st.session_state:
    st.session_state.planejamento = carregar_dados(ARQUIVO_PLAN, [])

# --- MENU LATERAL DE NAVEGAÇÃO ---
st.sidebar.title("⚙️ Gestão de Manutenção")
menu = st.sidebar.radio("Navegar para:", [
    "📋 Cadastro & Edição de Máquinas", 
    "📅 Planejamento & Checklists", 
    "📜 Histórico de Trocas", 
    "⚠️ Emissão de PT"
])

# --- EXIBIÇÃO DO LOGO SUPERIOR ---
img_logo_b64 = obter_base64_imagem("logo.png")
if img_logo_b64:
    st.markdown(f'<img src="data:image/png;base64,{img_logo_b64}" style="width:200px; margin-bottom:20px;">', unsafe_allow_html=True)

# ==========================================
# 1. CADASTRO, EDIÇÃO E EXCLUSÃO
# ==========================================
if menu == "📋 Cadastro & Edição de Máquinas":
    st.header("📋 Gerenciamento de Máquinas e Equipamentos")
    aba_lista, aba_cadastrar, aba_editar = st.tabs(["🔍 Ver e Excluir", "➕ Cadastrar Novo", "✏️ Editar Existente"])
    
    with aba_lista:
        st.subheader("Equipamentos Registrados no Sistema")
        if not st.session_state.equipamentos:
            st.info("Nenhum equipamento cadastrado.")
        else:
            for eq in st.session_state.equipamentos:
                st.write(f"🔹 **[{eq['id']}] {eq['nome']}** | Setor: {eq['localizacao']} | Criticidade: {eq['criticidade']}")
                if st.button(f"🗑️ Remover {eq['id']}", key=f"del_{eq['id']}"):
                    st.session_state.equipamentos = [e for e in st.session_state.equipamentos if e['id'] != eq['id']]
                    salvar_dados(ARQUIVO_EQ, st.session_state.equipamentos)
                    st.success(f"Equipamento {eq['id']} removido com sucesso!")
                    st.rerun()
                st.write("---")
                        
    with aba_cadastrar:
        st.subheader("Cadastrar Nova Máquina")
        with st.form("form_cadastro"):
            id_eq = st.text_input("Código/Tag do Equipamento (Ex: EQ-003):")
            nome_eq = st.text_input("Nome do Equipamento:")
            local_eq = st.text_input("Localização / Setor:")
            crit_eq = st.selectbox("Criticidade:", ["Baixa", "Média", "Alta"])
            st.markdown("---")
            st.subheader("📋 Definição dos Itens Fixos de Preventiva (Coloque um por linha):")
            c_sem = st.text_area("Itens da Preventiva Semanal:", "Verificar nível de óleo\nLimpeza geral")
            c_mes = st.text_area("Itens da Preventiva Mensal:", "Trocar filtros\nConferir correias")
            c_ano = st.text_area("Itens da Preventiva Anual:", "Revisão geral do motor")
            
            if st.form_submit_button("Salvar Equipamento"):
                if id_eq and nome_eq:
                    if any(e['id'] == id_eq for e in st.session_state.equipamentos):
                        st.error("Já existe um equipamento cadastrado com este Código/Tag.")
                    else:
                        st.session_state.equipamentos.append({
                            "id": id_eq, "nome": nome_eq, "localizacao": local_eq, "criticidade": crit_eq,
                            "check_semanal": c_sem, "check_mensal": c_mes, "check_anual": c_ano
                        })
                        salvar_dados(ARQUIVO_EQ, st.session_state.equipamentos)
                        st.success("Equipamento adicionado com sucesso!")
                        st.rerun()
                else:
                    st.error("Por favor, preencha o Código e o Nome.")

    with aba_editar:
        st.subheader("Editar Máquina Existente")
        if not st.session_state.equipamentos:
            st.info("Nenhum equipamento disponível para edição.")
        else:
            opcoes_edicao = {f"{e['id']} - {e['nome']}": e for e in st.session_state.equipamentos}
            selecionado_edicao = st.selectbox("Selecione qual máquina deseja alterar:", list(opcoes_edicao.keys()))
            eq_para_editar = opcoes_edicao[selecionado_edicao]
            
            with st.form("form_edicao"):
                novo_nome = st.text_input("Nome do Equipamento:", value=eq_para_editar['nome'])
                novo_local = st.text_input("Localização / Setor:", value=eq_para_editar['localizacao'])
                novo_crit = st.selectbox("Criticidade:", ["Baixa", "Média", "Alta"], index=["Baixa", "Média", "Alta"].index(eq_para_editar['criticidade']))
                st.markdown("---")
                st.subheader("✏️ Editar Itens de Verificação da Máquina:")
                n_sem = st.text_area("Preventiva Semanal:", value=eq_para_editar.get('check_semanal', ''))
                n_mes = st.text_area("Preventiva Mensal:", value=eq_para_editar.get('check_mensal', ''))
                n_ano = st.text_area("Preventiva Anual:", value=eq_para_editar.get('check_anual', ''))
                
                if st.form_submit_button("Gravar Alterações"):
                    for e in st.session_state.equipamentos:
                        if e['id'] == eq_para_editar['id']:
                            e['nome'] = novo_nome
                            e['localizacao'] = novo_local
                            e['criticidade'] = novo_crit
                            e['check_semanal'] = n_sem
                            e['check_mensal'] = n_mes
                            e['check_anual'] = n_ano
                    salvar_dados(ARQUIVO_EQ, st.session_state.equipamentos)
                    st.success("Alterações salvas com sucesso!")
                    st.rerun()

# ==========================================
# 2. PLANEJAMENTO TEMPORAL
# ==========================================
elif menu == "📅 Planejamento & Checklists":
    st.header("📅 Planejamento de Manutenções Preventivas")
    aba_sem, aba_mes, aba_ano, aba_novo = st.tabs(["🗓️ Semanal", "📅 Mensal", "⏳ Anual", "➕ Agendar Preventiva"])
    
    def exibir_itens(frequencia, chave_check):
        dados = [p for p in st.session_state.planejamento if p['periodo'] == frequencia and p['status'] == "Pendente"]
        if dados:
            for p in dados:
                st.write(f"⚙️ **{p['equipamento']}** | **Status:** {p['status']}")
                st.write(f"🔧 Peças Programadas para Troca: {p['pecas']}")
                maq = next((e for e in st.session_state.equipamentos if e['nome'] == p['equipamento']), None)
                if maq and maq.get(chave_check):
                    st.caption("📋 **Itens Específicos que serão verificados nesta máquina:**")
                    for item in maq[chave_check].split('\n'):
                        if item.strip():
                            st.caption(f" ▢ {item.strip()}")
                st.write("---")
        else:
            st.info(f"Nenhuma manutenção pendente para o período {frequencia}.")

    with aba_sem:
        exibir_itens("Semanal", "check_semanal")
    with aba_mes:
        exibir_itens("Mensal", "check_mensal")
    with aba_ano:
        exibir_itens("Anual", "check_anual")
    with aba_novo:
        # SOLUÇÃO DEFINITIVA: Remoção completa do bloco condicional com 'else:' na linha 214
        if not st.session_state.equipamentos:
