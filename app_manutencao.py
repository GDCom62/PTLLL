import streamlit as st
from datetime import datetime

# Configuração da página para layout amplo
st.set_page_config(page_title="Controle de Manutenção & PT", layout="wide", page_icon="⚙️")

# --- INICIALIZAÇÃO DO BANCO DE DADOS TEMPORÁRIO (SESSION STATE) ---
if "equipamentos" not in st.session_state:
    st.session_state.equipamentos = [
        {"id": "EQ-001", "nome": "Torno Mecânico Nardini", "localizacao": "Oficina Central", "criticidade": "Alta"},
        {"id": "EQ-002", "nome": "Compressor de Ar Schulz", "localizacao": "Sala de Compressores", "criticidade": "Média"},
    ]

if "historico" not in st.session_state:
    st.session_state.historico = [
        {"data": "2026-05-10", "equipamento": "Torno Mecânico Nardini", "tipo": "Corretiva", "descricao": "Troca de correia dentada", "executor": "Carlos Silva"}
    ]

if "planejamento" not in st.session_state:
    st.session_state.planejamento = [
        {"id": 1, "equipamento": "Torno Mecânico Nardini", "periodo": "Semanal", "pecas": "Filtro de óleo", "status": "Pendente", "seguranca": "Uso obrigatório de óculos de proteção e bota de segurança. Desenergizar o equipamento (Lockout/Tagout)."},
        {"id": 2, "equipamento": "Compressor de Ar Schulz", "periodo": "Mensal", "pecas": "Óleo lubrificante e purgador", "status": "Pendente", "seguranca": "Aliviar pressão interna do sistema antes de iniciar. Bloquear chave geral elétrica."}
    ]

# --- MENU LATERAL DE NAVEGAÇÃO ---
st.sidebar.title("⚙️ Gestão de Manutenção")
menu = st.sidebar.radio("Navegar para:", ["Catálogo de Equipamentos", "Planejamento (Semanal/Mensal/Anual)", "Histórico de Serviços", "Emissão de Permissão de Trabalho (PT)"])

# --- 1. CATÁLOGO DE EQUIPAMENTOS ---
if menu == "Catálogo de Equipamentos":
    st.header("📋 Catálogo de Máquinas e Equipamentos")
    
    with st.expander("➕ Cadastrar Novo Equipamento"):
        with st.form("form_equipamento"):
            col1, col2 = st.columns(2)
            with col1:
                id_eq = st.text_input("Código/Tag do Equipamento:")
                nome_eq = st.text_input("Nome do Equipamento:")
            with col2:
                local_eq = st.text_input("Localização / Setor:")
                crit_eq = st.selectbox("Criticidade:", ["Baixa", "Média", "Alta"])
            
            if st.form_submit_button("Salvar Equipamento"):
                if id_eq and nome_eq:
                    st.session_state.equipamentos.append({"id": id_eq, "nome": nome_eq, "localizacao": local_eq, "criticidade": crit_eq})
                    st.success("Equipamento cadastrado com sucesso!")
                    st.rerun()
                else:
                    st.error("Preencha o Código e o Nome do equipamento.")

    # Exibição usando tabela nativa do Streamlit (aceita listas de dicionários)
    st.table(st.session_state.equipamentos)

# --- 2. PLANEJAMENTO (SEMANAL, MENSAL, ANUAL) ---
elif menu == "Planejamento (Semanal/Mensal/Anual)":
    st.header("📅 Planejamento de Manutenções Preventivas")
    
    aba_sem, aba_mes, aba_ano, aba_novo = st.tabs(["🗓️ Semanal", "📅 Mensal", "⏳ Anual", "➕ Agendar Preventiva"])
    
    def exibir_tabela_periodo(frequencia):
        dados_filtrados = [p for p in st.session_state.planejamento if p['periodo'] == frequencia]
        if dados_filtrados:
            st.table(dados_filtrados)
        else:
            st.info(f"Nenhuma manutenção programada para o período {frequencia}.")

    with aba_sem:
        st.subheader("Manutenções Semanais")
        exibir_tabela_periodo("Semanal")
        
    with aba_mes:
        st.subheader("Manutenções Mensais")
        exibir_tabela_periodo("Mensal")
        
    with aba_ano:
        st.subheader("Manutenções Anuais")
        exibir_tabela_periodo("Anual")

    with aba_novo:
        with st.form("form_planejamento"):
            eq_escolhido = st.selectbox("Selecione o Equipamento:", [e['nome'] for e in st.session_state.equipamentos])
            periodo_escolhido = st.selectbox("Período/Frequência:", ["Semanal", "Mensal", "Anual"])
            pecas_necessarias = st.text_area("Descrição das Peças a serem Trocadas:")
            regras_seguranca = st.text_area("Instruções de Segurança Específicas (EPI/Procedimento):")
            
            if st.form_submit_button("Salvar no Planejamento"):
                novo_id = len(st.session_state.planejamento) + 1
                st.session_state.planejamento.append({
                    "id": novo_id, "equipamento": eq_escolhido, "periodo": periodo_escolhido,
                    "pecas": pecas_necessarias, "status": "Pendente", "seguranca": regras_seguranca
                })
                st.success("Manutenção programada com sucesso!")
                st.rerun()

# --- 3. HISTÓRICO DE SERVIÇOS ---
elif menu == "Histórico de Serviços":
    st.header("📜 Histórico de Manutenções Realizadas")
    if st.session_state.historico:
        st.table(st.session_state.historico)
    else:
        st.info("Nenhum registro encontrado no histórico.")

# --- 4. PERMISSÃO DE TRABALHO (PT) ---
elif menu == "Emissão de Permissão de Trabalho (PT)":
    st.header("⚠️ Emissão de Permissão de Trabalho (PT)")
    st.write("Selecione uma ordem planejada para gerar o documento oficial de segurança.")

    opcoes_pt = {f"{p['id']} - {p['equipamento']} ({p['periodo']})": p for p in st.session_state.planejamento if p['status'] == "Pendente"}
    
    if opcoes_pt:
        selecao = st.selectbox("Selecione a Manutenção Pendente:", list(opcoes_pt.keys()))
        manutencao_selecionada = opcoes_pt[selecao]
        
        st.subheader("Dados de Execução")
        colaborador = st.text_input("Nome Nominal do Colaborador Executante:")
        data_execucao = st.date_input("Data de Execução:")
        
        if st.button("Gerar Permissão de Trabalho Oficial"):
            if colaborador:
                local = next((e['localizacao'] for e in st.session_state.equipamentos if e['nome'] == manutencao_selecionada['equipamento']), "Não Informado")
                
                st.markdown("---")
                st.markdown(f"""
                <div style="border: 2px solid #FF4B4B; padding: 20px; border-radius: 10px; background-color: #FFF5F5; color: #000000;">
                    <h2 style="text-align: center; color: #FF4B4B; margin-top:0;">⚠️ PERMISSÃO DE TRABALHO (PT) - Nº 00{manutencao_selecionada['id']}</h2>
                    <hr style="border: 1px solid #FF4B4B;">
                    <p><strong>Status:</strong> <span style="color: green; font-weight: bold;">AUTORIZADO</span></p>
                    <p><strong>Colaborador Autorizado (Nominal):</strong> {colaborador}</p>
                    <p><strong>Data de Validade:</strong> {data_execucao.strftime('%d/%m/%Y')}</p>
                    <hr style="border: 0.5px dashed #FF4B4B;">
                    <p><strong>Equipamento:</strong> {manutencao_selecionada['equipamento']}</p>
                    <p><strong>Local da Manutenção:</strong> {local}</p>
                    <p><strong>Peças Programadas para Troca:</strong> {manutencao_selecionada['pecas']}</p>
                    <hr style="border: 0.5px dashed #FF4B4B;">
                    <h4 style="color: #FF4B4B; margin-bottom: 5px;">🛑 DESCRITIVO DE SEGURANÇA E ANÁLISE DE RISCO:</h4>
                    <p style="background-color: #FFE6E6; padding: 10px; border-left: 5px solid #FF4B4B;">{manutencao_selecionada['seguranca']}</p>
                    <br><br>
                    <div style="display: flex; justify-content: space-between;">
                        <p style="border-top: 1px solid #000; width: 45%; text-align: center;"><small>Assinatura do Supervisor / Emitente</small></p>
                        <p style="border-top: 1px solid #000; width: 45%; text-align: center;"><small>Assinatura do Executante: {colaborador}</small></p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("Finalizar Serviço e Gravar no Histórico"):
                    st.session_state.historico.append({
                        "data": str(data_execucao),
                        "equipamento": manutencao_selecionada['equipamento'],
                        "tipo": f"Preventiva ({manutencao_selecionada['periodo']})",
                        "descricao": f"Troca de: {manutencao_selecionada['pecas']}",
                        "executor": colaborador
                    })
                    for p in st.session_state.planejamento:
                        if p['id'] == manutencao_selecionada['id']:
                            p['status'] = "Concluído"
                    st.success("Manutenção concluída e enviada ao histórico!")
                    st.rerun()
            else:
                st.error("Por favor, digite o nome nominal do colaborador antes de gerar a PT.")
    else:
        st.info("Não existem manutenções pendentes de emissão de PT no momento.")
