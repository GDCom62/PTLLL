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
            
    # Dados padrão de fábrica
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
            {"id": 1, "equipamento": "Torno Mecânico Nardini", "periodo": "Semanal", "data_prevista": datetime.now().strftime("%d/%m/%Y"), "pecas": "Troca de oleo das guias e limpeza dos barramentos", "status": "Pendente", "seguranca": "Cuidado com partes giratorias."}
        ],
        "historico": [
            {"id": 99, "equipamento": "Compressor de Ar Schulz", "periodo": "Mensal", "data_prevista": "15/05/2026", "data_conclusao": "15/05/2026 10:00", "pecas": "Troca de filtro de ar", "status": "Concluido"}
        ]
    }
    salvar_dados(dados_padrao)
    return dados_padrao

def salvar_dados(dados):
    """Salva fisicamente as listas no arquivo local permanente em disco."""
    with open(ARQUIVO_BANCO, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

# Sincroniza o banco de dados permanente com os estados de sessão do Streamlit
if "db" not in st.session_state:
    st.session_state.db = carregar_dados()

# Mantém os nomes originais que as suas variáveis chamavam
st.session_state.maquinas = st.session_state.db["maquinas"]
st.session_state.planejamento = st.session_state.db["planejamento"]
st.session_state.historico = st.session_state.db["historico"]

# --- MENU LATERAL E LOGO ---
if os.path.exists("logo.png"):
    st.sidebar.image("logo.png", use_column_width=True)
else:
    st.sidebar.info("💡 Para exibir sua logo, adicione o arquivo 'logo.png' no GitHub.")

st.sidebar.markdown("**Desenvolvido por GDCOM**")
st.sidebar.title("⚙️ Gestão de Manutenção")
menu = st.sidebar.radio("Navegar para:", [
    "🔍 Lista de Máquinas",
    "➕ Cadastrar Nova Máquina",
    "📅 Planejamento & Checklists",
    "📜 Histórico de Trocas",
    "⚠️ Emissão de PT"
])

equipamentos = st.session_state.maquinas
todos_agendamentos = st.session_state.planejamento
historico_lista = st.session_state.historico

# ==========================================
# ABAS DO SISTEMA
# ==========================================
if menu == "🔍 Lista de Máquinas":
    st.header("🔍 Equipamentos Registrados")
    for idx, eq in enumerate(equipamentos):
        st.write(f"🔹 **[{eq.get('id', idx)}] {eq.get('nome')}** | Setor: {eq.get('localizacao')} | Criticidade: {eq.get('criticidade')}")
        st.write("---")

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

elif menu == "📅 Planejamento & Checklists":
    st.header("📅 Planejamento de Manutenções Preventivas")
    st.subheader("📋 Consulta Rápida de Ações Preventivas")
    opcoes_lista = {eq.get('nome', 'Máquina'): eq for eq in equipamentos}
    maquina_selecionada = st.selectbox("Selecione uma máquina:", list(opcoes_lista.keys()))
    
    if maquina_selecionada:
        dados_mq = opcoes_lista[maquina_selecionada]
        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1: st.info(f"**Semanal:**\n{dados_mq.get('check_semanal', 'Nao configurado.')}")
        with col_c2: st.warning(f"**Mensal:**\n{dados_mq.get('check_mes', 'Nao configurado.')}")
        with col_c3: st.error(f"**Anual:**\n{dados_mq.get('check_anual', 'Nao configurado.')}")
            
    st.markdown("---")
    st.subheader("📅 Agendar Nova Intervenção")
    with st.form("form_agenda_direto"):
        lista_nomes = list(opcoes_lista.keys())
        eq_escolhido = st.selectbox("Selecione a Máquina Alvo:", lista_nomes if lista_nomes else ["Nenhum cadastrado"])
        periodo_escolhido = st.selectbox("Escolha o Período:", ["Semanal", "Mensal", "Anual"])
        data_planejada = st.date_input("Selecione a Data:", datetime.now())
        pecas_necessarias = st.text_area("Descrição das Peças / Ferramentas / Escopo:", value="Realizar rotina padrao de preventiva.")
        botao_agenda = st.form_submit_button("💾 Gravar e Agendar Manutenção")
        
    if botao_agenda and eq_escolhido != "Nenhum cadastrado":
        novo_agendamento = {"id": len(todos_agendamentos) + 1, "equipamento": eq_escolhido, "periodo": periodo_escolhido, "data_prevista": data_planejada.strftime("%d/%m/%Y"), "pecas": pecas_necessarias, "status": "Pendente", "seguranca": ""}
        st.session_state.db["planejamento"].append(novo_agendamento)
        salvar_dados(st.session_state.db)
        st.success("🎉 Agendamento gravado com sucesso!")
        st.rerun()

    st.markdown("---")
    st.subheader("🔍 Ordens de Serviço Abertas")
    ordens_exibicao = [os for os in todos_agendamentos if os.get("status") == "Pendente"]
    
    for idx, p in enumerate(ordens_exibicao):
        st.write(f"⚙️ **{p.get('equipamento')}** | Período: **{p.get('periodo')}** | 📅 **Prevista:** {p.get('data_prevista')}")
        st.write(f"🔧 Peças/Ferramentas: {p.get('pecas')}")
        if st.button("✔️ Concluir OS e Enviar para Histórico", key=f"comp_{idx}"):
            registro_h = {"id": p.get('id'), "equipamento": p.get('equipamento'), "periodo": p.get('periodo'), "data_prevista": p.get('data_prevista'), "data_conclusao": datetime.now().strftime("%d/%m/%Y %H:%M"), "pecas": p.get('pecas'), "status": "Concluido"}
            st.session_state.db["historico"].append(registro_h)
            for item in st.session_state.db["planejamento"]:
                if item.get("id") == p.get("id"):
                    item["status"] = "Concluido"
                    break
            salvar_dados(st.session_state.db)
            st.success("Ordem finalizada e salva!")
            st.rerun()
        st.write("---")

elif menu == "📜 Histórico de Trocas":
    st.header("📜 Histórico de Serviços Concluídos")
    st.subheader("📊 Gráfico de Evolução dos Serviços por Período")
    
    ordens_abertas = [os for os in todos_agendamentos if os.get("status") == "Pendente"]
    p_semanal = sum(1 for x in ordens_abertas if str(x.get('periodo')).lower() == 'semanal')
    p_mensal = sum(1 for x in ordens_abertas if str(x.get('periodo')).lower() == 'mensal')
    p_anual = sum(1 for x in ordens_abertas if str(x.get('periodo')).lower() == 'anual')
    
    c_semanal = sum(1 for x in historico_lista if str(x.get('periodo')).lower() == 'semanal')
    c_mensal = sum(1 for x in historico_lista if str(x.get('periodo')).lower() == 'mensal')
    c_anual = sum(1 for x in historico_lista if str(x.get('periodo')).lower() == 'anual')
    
    dados_grafico = {
        "Período": ["Semanal", "Mensal", "Anual"],
        "Pendentes (Abertas)": [p_semanal, p_mensal, p_anual],
        "Concluídos (Histórico)": [c_semanal, c_mensal, c_anual]
    }
    df = pd.DataFrame(dados_grafico).set_index("Período")
    st.bar_chart(df)
    
    st.markdown("---")
