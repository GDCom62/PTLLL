import streamlit as st
from datetime import datetime
import os
import json
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Controle de Manutenção & PT", layout="wide", page_icon="⚙️")

# --- BANCO DE DADOS PERSISTENTE EM ARQUIVO LOCAL (JSON) ---
ARQUIVO_BANCO = "banco_manutencao.json"

def carregar_dados():
    """Carrega os dados salvos em arquivo local. Se não existir, cria o padrão."""
    if os.path.exists(ARQUIVO_BANCO):
        try:
            with open(ARQUIVO_BANCO, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
            
    # Dados padrão de fábrica com chaves e períodos totalmente padronizados em minúsculo
    dados_padrao = {
        "maquinas": [
            {
                "id": "EQ-001", 
                "nome": "Torno Mecânico Nardini", 
                "localizacao": "Oficina Central", 
                "criticidade": "Alta", 
                "check_semanal": "1. Verificar nivel de oleo lubrificante; 2. Limpar os barramentos; 3. Lubrificar as guias lineares; 4. Remover cavacos acumulados.", 
                "check_mensal": "1. Trocar filtros de fluido refrigerante; 2. Conferir tensao das correias do motor; 3. Verificar folgas nos eixos X e Z; 4. Testar botoes de emergencia.", 
                "check_anual": "1. Revisao geral do motor eletrico; 2. Alinhamento geometrico completo; 3. Troca total do oleo da caixa de engrenagens; 4. Megagem de isolamento eletrico."
            },
            {
                "id": "EQ-002", 
                "nome": "Compressor de Ar Schulz", 
                "localizacao": "Sala de Compressores", 
                "criticidade": "Média", 
                "check_semanal": "1. Drenar condensado do reservatorio; 2. Verificar nivel de oleo do carter; 3. Checar ruidos ou vibracoes estranhas; 4. Verificar pressao de operacao.", 
                "check_mensal": "1. Limpar e inspecionar o filtro de ar; 2. Verificar vazamentos em conexoes e tubulacoes; 3. Conferir alinhamento das polias e correias; 4. Testar pressostato.", 
                "check_anual": "1. Troca completa do oleo lubrificante; 2. Substituicao do elemento do filtro de ar; 3. Teste hidrostatico e calibracao da valvula de seguranca; 4. Limpeza interna das serpentinas."
            }
        ],
        "planejamento": [
            {"id": 1, "equipamento": "Torno Mecânico Nardini", "periodo": "semanal", "data_prevista": datetime.now().strftime("%d/%m/%Y"), "pecas": "Troca de oleo das guias e limpeza dos barramentos", "status": "Pendente", "seguranca": "Cuidado com partes giratorias."}
        ],
        "historico": [
            {"id": 99, "equipamento": "Compressor de Ar Schulz", "periodo": "mensal", "data_prevista": "15/05/2026", "data_conclusao": "15/05/2026 10:00", "pecas": "Troca de filtro de ar", "status": "Concluido"}
        ]
    }
    salvar_dados(dados_padrao)
    return dados_padrao

def salvar_dados(dados):
    """Salva fisicamente as listas no arquivo local permanente em disco."""
    with open(ARQUIVO_BANCO, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

# Força o recarregamento limpo do banco de dados na inicialização
st.session_state.db = carregar_dados()

st.session_state.maquinas = st.session_state.db["maquinas"]
st.session_state.planejamento = st.session_state.db["planejamento"]
st.session_state.historico = st.session_state.db["historico"]

if "editando_os_id" not in st.session_state:
    st.session_state.editando_os_id = None

# --- MENU LATERAL ---
st.sidebar.markdown("**Desenvolvido por GDCOM**")
st.sidebar.title("⚙️ Gestão de Manutenção")
menu = st.sidebar.radio("Navegar para:", [
    "🔍 Lista de Máquinas",
    "➕ Cadastrar Nova Máquina",
    "📅 Planejamento & Ordens de Serviço (OS)",
    "📜 Histórico de Trocas",
    "⚠️ Emissão de PT"
])

equipamentos = st.session_state.maquinas
todos_agendamentos = st.session_state.planejamento
historico_lista = st.session_state.historico

# ==========================================
# ABA 1: LISTA DE MÁQUINAS
# ==========================================
if menu == "🔍 Lista de Máquinas":
    st.header("🔍 Equipamentos Registrados")
    for idx, eq in enumerate(equipamentos):
        st.write(f"🔹 **[{eq.get('id', idx)}] {eq.get('nome')}** | Setor: {eq.get('localizacao')} | Criticidade: {eq.get('criticidade')}")
        st.write("---")

# ==========================================
# ABA 2: CADASTRAR NOVA MÁQUINA
# ==========================================
elif menu == "➕ Cadastrar Nova Máquina":
    st.header("➕ Cadastrar Nova Máquina")
    with st.form("form_cadastro_direto"):
        id_eq = st.text_input("Código/Tag do Equipamento (Ex: EQ-003):")
        nome_eq = st.text_input("Nome do Equipamento:")
        local_eq = st.text_input("Localização / Setor:")
        crit_eq = st.selectbox("Criticidade:", ["Baixa", "Média", "Alta"])
        st.markdown("##### 📜 Ações Preventivas Recomendadas")
        c_sem = st.text_area("Checklist Semanal:", "1. Verificar nivel de oleo; 2. Limpeza geral")
        c_mes = st.text_area("Checklist Mensal:", "1. Trocar filtros; 2. Conferir correias")
        c_ano = st.text_area("Checklist Anual:", "1. Revisao geral do motor")
        botao_salvar = st.form_submit_button("Salvar Equipamento")
        
    if botao_salvar and id_eq and nome_eq:
        payload = {"id": id_eq, "nome": nome_eq, "localizacao": local_eq, "criticidade": crit_eq, "check_semanal": c_sem, "check_mes": c_mes, "check_anual": c_ano}
        st.session_state.db["maquinas"].append(payload)
        salvar_dados(st.session_state.db)
        st.success("🎉 Equipamento gravado permanentemente em disco!")
        st.rerun()

# ==========================================
# ABA 3: PLANEJAMENTO E ORDENS DE SERVIÇO (OS)
# ==========================================
elif menu == "📅 Planejamento & Ordens de Serviço (OS)":
    st.header("📅 Planejamento & Ordens de Serviço (OS)")
    
    if st.session_state.editando_os_id is not None:
        st.subheader("📝 Editar Ordem de Serviço Ativa")
        os_para_editar = next((item for item in st.session_state.db["planejamento"] if item["id"] == st.session_state.editando_os_id), None)
        
        if os_para_editar:
            with st.form("form_editar_os"):
                edit_equip = st.selectbox("Máquina Alvo:", [eq["nome"] for eq in equipamentos], index=[eq["nome"] for eq in equipamentos].index(os_para_editar["equipamento"]) if os_para_editar["equipamento"] in [eq["nome"] for eq in equipamentos] else 0)
                edit_periodo = st.selectbox("Escolha o Período:", ["Semanal", "Mensal", "Anual"], index=["semanal", "mensal", "anual"].index(os_para_editar["periodo"].lower()))
                edit_data = st.date_input("Selecione a Data:", datetime.strptime(os_para_editar["data_prevista"], "%d/%m/%Y"))
                edit_pecas = st.text_area("Descrição / Escopo do Serviço:", value=os_para_editar["pecas"])
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1: gravar_edicao = st.form_submit_button("💾 Salvar Alterações na OS")
                with col_btn2: cancelar_edicao = st.form_submit_button("❌ Cancelar Edição")
            
            if gravar_edicao:
                os_para_editar["equipamento"] = edit_equip
                os_para_editar["periodo"] = edit_periodo.lower()
                os_para_editar["data_prevista"] = edit_data.strftime("%d/%m/%Y")
                os_para_editar["pecas"] = edit_pecas
                salvar_dados(st.session_state.db)
                st.session_state.editando_os_id = None
                st.success("🎉 Alterações gravadas com sucesso!")
                st.rerun()
                
            if cancelar_edicao:
                st.session_state.editando_os_id = None
                st.rerun()
    else:
        st.subheader("📅 Agendar Nova Manutenção / Gerar OS")
        with st.form("form_agenda_direto"):
            lista_nomes = [eq["nome"] for eq in equipamentos]
            eq_escolhido = st.selectbox("Selecione a Máquina Alvo:", lista_nomes if lista_nomes else ["Nenhum cadastrado"])
            periodo_escolhido = st.selectbox("Escolha o Período:", ["Semanal", "Mensal", "Anual"])
            data_planejada = st.date_input("Selecione a Data:", datetime.now())
            pecas_necessarias = st.text_area("Descrição das Peças / Ferramentas / Escopo:", value="Realizar rotina padrao de preventiva.")
            botao_agenda = st.form_submit_button("💾 Gravar e Gerar OS Pendente")
            
        if botao_agenda and eq_escolhido != "Nenhum cadastrado":
            novo_id = max([item["id"] for item in todos_agendamentos], default=0) + 1
            novo_agendamento = {"id": novo_id, "equipamento": eq_escolhido, "periodo": periodo_escolhido.lower(), "data_prevista": data_planejada.strftime("%d/%m/%Y"), "pecas": pecas_necessarias, "status": "Pendente", "seguranca": ""}
            st.session_state.db["planejamento"].append(novo_agendamento)
            salvar_dados(st.session_state.db)
            st.success(f"🎉 Ordem de Serviço OS #{novo_id} gerada e salva permanentemente!")
            st.rerun()

    st.markdown("---")
    st.subheader("🔍 Painel de Controle de Ordens de Serviço (Abertas)")
    ordens_exibicao = [os for os in todos_agendamentos if os.get("status") == "Pendente"]
    
    if not ordens_exibicao:
        st.info("Nenhuma Ordem de Serviço aberta no momento.")
    else:
        for p in ordens_exibicao:
            st.markdown(f"#### 🛠️ OS #{p.get('id')} - {p.get('equipamento')} ({str(p.get('periodo')).upper()})")
            st.write(f"📅 **Data Prevista:** {p.get('data_prevista')} | 🔧 **Escopo:** {p.get('pecas')}")
            
            col_b1, col_b2, col_b3 = st.columns(3)
            with col_b1:
                if st.button("✔️ Concluir e Fechar OS", key=f"concluir_{p.get('id')}"):
