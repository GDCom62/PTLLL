import streamlit as st
from datetime import datetime
import os
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Controle de Manutenção & PT", layout="wide", page_icon="⚙️")

# --- INICIALIZAÇÃO FIXA DA MEMÓRIA DE SEGURANÇA LOCAL ---
if "maquinas_locais" not in st.session_state:
    st.session_state.maquinas_locais = [
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
    ]

if "planejamento_local" not in st.session_state:
    st.session_state.planejamento_local = [
        {"id": 1, "equipamento": "Torno Mecânico Nardini", "periodo": "Semanal", "data_prevista": datetime.now().strftime("%d/%m/%Y"), "pecas": "Troca de oleo das guias e limpeza dos barramentos", "status": "Pendente"}
    ]

if "historico_local" not in st.session_state:
    st.session_state.historico_local = [
        {"id": 99, "equipamento": "Compressor de Ar Schulz", "periodo": "Mensal", "data_prevista": "15/05/2026", "data_conclusao": "15/05/2026 10:00", "pecas": "Troca de filtro de ar", "status": "Concluido"}
    ]

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

equipamentos = list(st.session_state.maquinas_locais)
todos_agendamentos = list(st.session_state.planejamento_local)
historico_lista = list(st.session_state.historico_local)

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
        st.session_state.maquinas_locais.append(payload)
        st.success("🎉 Equipamento salvo com sucesso!")
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
        novo_agendamento = {"id": len(todos_agendamentos) + 1, "equipamento": eq_escolhido, "periodo": periodo_escolhido, "data_prevista": data_planejada.strftime("%d/%m/%Y"), "pecas": pecas_necessarias, "status": "Pendente"}
        st.session_state.planejamento_local.append(novo_agendamento)
        st.success("🎉 Agendamento registrado!")
        st.rerun()

    st.markdown("---")
    st.subheader("🔍 Ordens de Serviço Abertas")
    for idx, p in enumerate(todos_agendamentos):
        st.write(f"⚙️ **{p.get('equipamento')}** | Período: **{p.get('periodo')}** | 📅 **Prevista:** {p.get('data_prevista')}")
        st.write(f"🔧 Peças/Ferramentas: {p.get('pecas')}")
        if st.button("✔️ Concluir OS e Enviar para Histórico", key=f"comp_{idx}"):
            registro_h = {"equipamento": p.get('equipamento'), "periodo": p.get('periodo'), "data_prevista": p.get('data_prevista'), "data_conclusao": datetime.now().strftime("%d/%m/%Y %H:%M"), "pecas": p.get('pecas'), "status": "Concluido"}
            st.session_state.historico_local.append(registro_h)
            st.session_state.planejamento_local = [item for item in st.session_state.planejamento_local if item.get('id') != p.get('id')]
            st.success("Ordem finalizada!")
            st.rerun()
        st.write("---")

elif menu == "⚠️ Emissão de PT":
    st.header("⚠️ Permissão de Trabalho (PT) & Segurança Industrial")
    
    if not todos_agendamentos or len(todos_agendamentos) == 0:
        st.warning("Não existem manutenções preventivas pendentes abertas para gerar PT.")
    else:
        opcoes_os = {f"OS #{p.get('id', idx)} - {p.get('equipamento')} ({p.get('periodo')})": p for idx, p in enumerate(todos_agendamentos)}
        os_selecionada = st.selectbox("Selecione a Ordem de Serviço Alvo:", list(opcoes_os.keys()))
        os_dados = opcoes_os[os_selecionada]
        
        mac_dados = next((m for m in equipamentos if m.get("nome") == os_dados.get("equipamento")), {})
        
        # MAPEAMENTO DIRETO VIA DICIONÁRIO (Evita completamente estruturas 'if/elif' e erros de indentação)
        periodo_chave = str(os_dados.get('periodo', '')).strip().lower()
        mapa_checklists = {
            "semanal": mac_dados.get("check_semanal", "Realizar rotina de inspecao semanal."),
            "mensal": mac_dados.get("check_mensal", "Realizar rotina de inspecao mensal."),
            "anual": mac_dados.get("check_anual", "Realizar rotina de inspecao anual.")
        }
        checklist_manutencao = mapa_checklists.get(periodo_chave, "Realizar rotina de inspecao padrao.")

        st.markdown("### 📝 Dados da Emissão")
        executante = st.text_input("Nome do Técnico Executante:", value="", placeholder="Digite o nome completo do técnico")
        emitente = st.text_input("Supervisor Emitente / Autorizador:", value="Supervisor de Manutenção")
        
        st.markdown("### 🚨 Análise Preliminar de Risco (APR)")
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1: r_altura = st.checkbox("Trabalho em Altura (NR-35)")
        with col_s2: r_eletrico = st.checkbox("Risco Elétrico / Painéis (NR-10)")
        with col_s3: r_quente = st.checkbox("Trabalho a Quente / Solda e Centelha")
        
        st.markdown("---")
        
        # Montagem dinâmica do bloco de NRs recomendadas
        recomendacoes_seguranca = "Seguir regras gerais de seguranca da planta operacional."
        if r_altura or r_eletrico or r_quente:
            recomendacoes_seguranca = ""
            if r_altura: 
                recomendacoes_seguranca += "• RECOMENDAÇÃO NR-35: Uso obrigatorio de cinto tipo paraquedista com duplo talabarte ancorado em linha de vida física. "
            if r_eletrico: 
