import streamlit as st
from datetime import datetime
import base64
import os
import json

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Controle de Manutenção & PT", layout="wide", page_icon="⚙️")

# --- SISTEMA DE BANCO DE DADOS PERSISTENTE (JSON) ---
ARQUIVO_BANCO = "dados_manutencao.json"

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

PLANEJAMENTO_PADRÃO = [
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

def carregar_banco_permanente():
    """Carrega os dados salvos no disco ou cria o arquivo inicial se ele não existir"""
    if os.path.exists(ARQUIVO_BANCO):
        try:
            with open(ARQUIVO_BANCO, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {"equipamentos": MÁQUINAS_PADRÃO.copy(), "planejamento": PLANEJAMENTO_PADRÃO.copy(), "historico": []}

def salvar_banco_permanente():
    """Grava as alterações da memória direto no arquivo físico do servidor"""
    dados = {
        "equipamentos": st.session_state.equipamentos,
        "planejamento": st.session_state.planejamento,
        "historico": st.session_state.historico
    }
    with open(ARQUIVO_BANCO, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

# Inicialização síncrona com o disco rígido da nuvem
if "dados_carregados" not in st.session_state:
    banco_fisico = carregar_banco_permanente()
    st.session_state.equipamentos = banco_fisico["equipamentos"]
    st.session_state.planejamento = banco_fisico["planejamento"]
    st.session_state.historico = banco_fisico["historico"]
    st.session_state.dados_carregados = True

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
        if st.session_state.equipamentos:
            for eq in list(st.session_state.equipamentos):
                st.write("🔹 **[" + str(eq['id'])+ "] " + str(eq['nome']) + "** | Setor: " + str(eq['localizacao']) + " | Criticidade: " + str(eq['criticidade']))
                if st.button("🗑️ Remover " + str(eq['id']), key="del_" + str(eq['id'])):
                    st.session_state.equipamentos = [e for e in st.session_state.equipamentos if e['id'] != eq['id']]
                    salvar_banco_permanente()
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
                    st.session_state.equipamentos.append({
                        "id": id_eq, "nome": nome_eq, "localizacao": local_eq, "criticidade": crit_eq,
                        "check_semanal": c_sem, "check_mensal": c_mes, "check_anual": c_ano
                    })
                    salvar_banco_permanente()
                    st.success("Máquina registrada com sucesso!")
                    st.rerun()
                else:
                    st.error("Preencha os campos obrigatórios.")

    with aba_editar:
        st.subheader("Editar Máquina Existente")
        opcoes_edicao = {e['id'] + " - " + e['nome']: e for e in st.session_state.equipamentos}
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
                    for e in st.session_state.equipamentos:
                        if e['id'] == eq_para_editar['id']:
                            e['nome'] = novo_nome
                            e['localizacao'] = novo_local
                            e['criticidade'] = novo_crit
                            e['check_semanal'] = n_sem
                            e['check_mensal'] = n_mes
                            e['check_anual'] = n_ano
                    salvar_banco_permanente()
                    st.success("Alterações salvas com sucesso!")
                    st.rerun()
