import streamlit as st
from datetime import datetime
import os
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Controle de Manutenção & PT", layout="wide", page_icon="⚙️")

# --- INICIALIZAÇÃO FIXA DA MEMÓRIA DE SEGURANÇA LOCAL ---
if "maquinas_locais" not in st.session_state:
    st.session_state.maquinas_locais = [
        {"id": "EQ-001", "nome": "Torno Mecânico Nardini", "localizacao": "Oficina Central", "criticidade": "Alta", "check_semanal": "Verificar nível de óleo, limpar barramento e lubrificar guias.", "check_mensal": "Trocar filtros de fluido, conferir tensão das correias.", "check_anual": "Revisão geral do motor elétrico e alinhamento geométrico."},
        {"id": "EQ-002", "nome": "Compressor de Ar Schulz", "localizacao": "Sala de Compressores", "criticidade": "Média", "check_semanal": "Drenar condensado do reservatório e checar ruídos estranhos.", "check_mensal": "Limpar/trocar filtro de ar, verificar vazamentos em conexões.", "check_anual": "Aferição do manômetro, teste de válvula de segurança e troca de óleo."}
    ]

if "planejamento_local" not in st.session_state:
    st.session_state.planejamento_local = [
        {"id": 1, "equipamento": "Torno Mecânico Nardini", "periodo": "Semanal", "data_prevista": datetime.now().strftime("%d/%m/%Y"), "pecas": "Inspeção preventiva padrão e lubrificação geral", "status": "Pendente"}
    ]

if "historico_local" not in st.session_state:
    st.session_state.historico_local = [
        {"id": 99, "equipamento": "Compressor de Ar Schulz", "periodo": "Mensal", "data_prevista": "15/05/2026", "data_conclusao": "15/05/2026 10:00", "pecas": "Troca de filtro de ar", "status": "Concluído"}
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
        c_sem = st.text_area("Checklist Semanal:", "Verificar nível de óleo\nLimpeza geral")
        c_mes = st.text_area("Checklist Mensal:", "Trocar filtros\nConferir correias")
        c_ano = st.text_area("Checklist Anual:", "Revisão geral do motor")
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
        with col_c1: st.info(f"**Semanal:**\n{dados_mq.get('check_semanal', 'Não configurado.')}")
        with col_c2: st.warning(f"**Mensal:**\n{dados_mq.get('check_mes', 'Não configurado.')}")
        with col_c3: st.error(f"**Anual:**\n{dados_mq.get('check_anual', 'Não configurado.')}")
            
    st.markdown("---")
    st.subheader("📅 Agendar Nova Intervenção")
    with st.form("form_agenda_direto"):
        lista_nomes = list(opcoes_lista.keys())
        eq_escolhido = st.selectbox("Selecione a Máquina Alvo:", lista_nomes if lista_nomes else ["Nenhum cadastrado"])
        periodo_escolhido = st.selectbox("Escolha o Período:", ["Semanal", "Mensal", "Anual"])
        data_planejada = st.date_input("Selecione a Data:", datetime.now())
        pecas_necessarias = st.text_area("Descrição das Peças / Ferramentas / Escopo:", value="Realizar rotina padrão de preventiva.")
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
            registro_h = {"equipamento": p.get('equipamento'), "periodo": p.get('periodo'), "data_prevista": p.get('data_prevista'), "data_conclusao": datetime.now().strftime("%d/%m/%Y %H:%M"), "pecas": p.get('pecas'), "status": "Concluído"}
            st.session_state.historico_local.append(registro_h)
            st.session_state.planejamento_local = [item for item in st.session_state.planejamento_local if item.get('id') != p.get('id')]
            st.success("Ordem finalizada!")
            st.rerun()
        st.write("---")

elif menu == "📜 Histórico de Trocas":
    st.header("📜 Histórico de Serviços Concluídos")
    st.subheader("📊 Gráfico de Evolução dos Serviços por Período")
    
    p_semanal = sum(1 for x in todos_agendamentos if str(x.get('periodo')).lower() == 'semanal')
    p_mensal = sum(1 for x in todos_agendamentos if str(x.get('periodo')).lower() == 'mensal')
    p_anual = sum(1 for x in todos_agendamentos if str(x.get('periodo')).lower() == 'anual')
    
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
    st.subheader("📋 Listagem Completa de Ordens Fechadas")
    for h in historico_lista:
        st.write(f"✅ **{h.get('equipamento')}** | Período: **{h.get('periodo')}**")
        st.write(f"⏱️ **Concluído em:** {h.get('data_conclusao', 'N/A')} | Intervenção realizada: {h.get('pecas')}")
        st.write("---")

elif menu == "⚠️ Emissão de PT":
    st.header("⚠️ Permissão de Trabalho (PT)")
    
    if not todos_agendamentos or len(todos_agendamentos) == 0:
        st.warning("Não existem manutenções pendentes no momento.")
    else:
        opcoes_os = {f"OS #{p.get('id', idx)} - {p.get('equipamento')}": p for idx, p in enumerate(todos_agendamentos)}
        os_selecionada = st.selectbox("Selecione a Ordem de Serviço:", list(opcoes_os.keys()))
        os_dados = opcoes_os[os_selecionada]
        
        executante = st.text_input("Nome do Técnico Executante:")
        emitente = st.text_input("Supervisor Emitente:", value="Supervisor de Manutenção")
        
        col_r1, col_r2 = st.columns(2)
        with col_r1: r_altura = st.checkbox("Trabalho em Altura (NR-35)")
        with col_r2: r_eletrico = st.checkbox("Risco Elétrico (NR-10)")
        
        st.markdown("---")
        # Grafia corrigida para evitar o erro de NameError
        ativar_pt = st.checkbox("🚨 Confirmar e Gerar Documento de PT")
        
        if ativar_pt:
            if not executante:
                st.error("❌ Digite o nome do técnico executante no campo acima para gerar o documento.")
            else:
                cod_doc = "PT-" + str(os_dados.get('id', '1')) + "-" + datetime.now().strftime("%M%S")
                riscos_str = ""
                if r_altura: riesgos_str = "[X] Altura (NR-35) "
                if r_eletrico: riscos_str += "[X] Elétrico (NR-10) "
                if not r_altura and not r_eletrico: riscos_str += "Nenhum risco crítico marcado"
                
                l1 = '<div style="border:3px double #FF4B4B; padding:20px; background-color:#FFF5F5; font-family:monospace; color:#000000; border-radius:5px; margin-top:15px;">'
                l2 = '<h3 style="text-align:center; color:#FF4B4B; margin-top:0;">⚠️ PERMISSÃO DE TRABALHO EMITIDA</h3>'
