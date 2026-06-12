import streamlit as st
import json
import os

st.set_page_config(page_title="Controle de Manutenção & PT", layout="wide", page_icon="⚙️")

# --- ARQUIVOS DE ARMAZENAMENTO COMPATÍVEIS (SEM PANDAS/NUMPY) ---
ARQUIVO_EQ = "dados_equipamentos.json"
ARQUIVO_PLAN = "dados_planejamento.json"
ARQUIVO_HIST = "dados_historico.json"

# --- FUNÇÕES DE CARGA E SALVAMENTO ---
def carregar_dados(arquivo, dados_padrao):
    if os.path.exists(arquivo):
        with open(arquivo, "r", encoding="utf-8") as f:
            return json.load(f)
    return dados_padrao

def salvar_dados(arquivo, dados):
    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

# --- INICIALIZAÇÃO DOS DADOS ---
if "equipamentos" not in st.session_state:
    st.session_state.equipamentos = carregar_dados(ARQUIVO_EQ, [
        {"id": "EQ-001", "nome": "Torno Mecânico Nardini", "localizacao": "Oficina Central", "criticidade": "Alta"},
        {"id": "EQ-002", "nome": "Compressor de Ar Schulz", "localizacao": "Sala de Compressores", "criticidade": "Média"},
    ])

if "historico" not in st.session_state:
    st.session_state.historico = carregar_dados(ARQUIVO_HIST, [
        {"data": "12/06/2026", "equipamento": "Torno Mecânico Nardini", "tipo": "Corretiva", "descricao": "Troca de correia dentada", "executor": "Carlos Silva", "pecas_trocadas": "Correia dentada industrial"}
    ])

if "planejamento" not in st.session_state:
    st.session_state.planejamento = carregar_dados(ARQUIVO_PLAN, [
        {"id": 1, "equipamento": "Torno Mecânico Nardini", "periodo": "Semanal", "pecas": "Filtro de óleo", "status": "Pendente", "seguranca": "Uso obrigatório de óculos de proteção. Desenergizar o equipamento (Lockout/Tagout)."},
        {"id": 2, "equipamento": "Compressor de Ar Schulz", "periodo": "Mensal", "pecas": "Óleo lubrificante", "status": "Pendente", "seguranca": "Aliviar pressão interna do sistema antes de iniciar. Bloquear chave geral elétrica."}
    ] )

# --- DICIONÁRIO FIXO DE CHECKLIST PREVENTIVO ---
CHECKLISTS_PADRAO = {
    "Semanal": [
        "Verificar nível de óleo e lubrificação geral",
        "Limpeza de resíduos e cavacos acumulados",
        "Conferir aperto de parafusos estruturais",
        "Testar botões de emergência e sensores de segurança"
    ],
    "Mensal": [
        "Trocar ou limpar filtros de ar / óleo",
        "Verificar tensão de correias e alinhamento de polias",
        "Inspecionar conexões elétricas e fiação no painel",
        "Medir temperatura de trabalho dos rolamentos e motor"
    ],
    "Anual": [
        "Revisão completa do motor elétrico e escovas",
        "Substituição integral do fluido hidráulico / lubrificante",
        "Calibração e aferição de instrumentos e manômetros",
        "Inspeção estrutural contra trincas, desgastes ou fadiga"
    ]
}

# --- MENU LATERAL DE NAVEGAÇÃO ---
st.sidebar.title("⚙️ Gestão de Manutenção")
menu = st.sidebar.radio("Navegar para:", [
    "Catálogo de Equipamentos", 
    "Planejamento & Checklists", 
    "Histórico de Trocas", 
    "Emissão de Permissão de Trabalho (PT)"
])

# 1. CATÁLOGO
if menu == "Catálogo de Equipamentos":
    st.header("📋 Catálogo de Máquinas e Equipamentos")
    with st.expander("➕ Cadastrar Novo Equipamento"):
        with st.form("form_equipamento"):
            id_eq = st.text_input("Código/Tag do Equipamento:")
            nome_eq = st.text_input("Nome do Equipamento:")
            local_eq = st.text_input("Localização / Setor:")
            crit_eq = st.selectbox("Criticidade:", ["Baixa", "Média", "Alta"])
            if st.form_submit_button("Salvar Equipamento"):
                if id_eq and nome_eq:
                    st.session_state.equipamentos.append({"id": id_eq, "nome": nome_eq, "localizacao": local_eq, "criticidade": crit_eq})
                    salvar_dados(ARQUIVO_EQ, st.session_state.equipamentos)
                    st.success("Equipamento cadastrado e salvo com sucesso!")
                    st.rerun()
                else:
                    st.error("Preencha o Código e o Nome.")
    
    for eq in st.session_state.equipamentos:
        st.write(f"🔹 **[{eq['id']}] {eq['nome']}** | Setor: {eq['localizacao']} | Criticidade: {eq['criticidade']}")

# 2. PLANEJAMENTO E CHECKLISTS FIXOS
elif menu == "Planejamento & Checklists":
    st.header("📅 Planejamento & Checklists Prévios de Verificação")
    aba_sem, aba_mes, aba_ano, aba_novo = st.tabs(["🗓️ Semanal", "📅 Mensal", "⏳ Anual", "➕ Agendar Preventiva"])
    
    def exibir_itens(frequencia):
        st.subheader(f"🔍 Checklist Prévio Fixo para Preventiva {frequencia}:")
        for item in CHECKLISTS_PADRAO[frequencia]:
            st.write(f"▢ {item}")
        
        st.markdown("---")
        st.subheader("📋 Ordens de Serviço Programadas:")
        dados = [p for p in st.session_state.planejamento if p['periodo'] == frequencia]
        if dados:
            for p in dados:
                st.write(f"⚙️ **{p['equipamento']}** | **Status:** {p['status']}")
                st.write(f"🔧 **Peças Previstas para Troca:** {p['pecas']}")
                st.caption(f"🛡️ Segurança: {p['seguranca']}")
                st.write("---")
        else:
            st.info(f"Nenhuma manutenção pendente para o período {frequencia}.")

    with aba_sem: exibir_itens("Semanal")
    with aba_mes: exibir_itens("Mensal")
    with aba_ano: exibir_itens("Anual")
    with aba_novo:
        with st.form("form_plan"):
            eq_escolhido = st.selectbox("Equipamento:", [e['nome'] for e in st.session_state.equipamentos])
            periodo_escolhido = st.selectbox("Período/Frequência:", ["Semanal", "Mensal", "Anual"])
            pecas_necessarias = st.text_area("Peças a serem Trocadas nesta preventiva:")
            regras_seguranca = st.text_area("Instruções de Segurança específicas:")
            if st.form_submit_button("Salvar no Planejamento"):
                st.session_state.planejamento.append({
                    "id": len(st.session_state.planejamento) + 1, "equipamento": eq_escolhido,
                    "periodo": periodo_escolhido, "pecas": pecas_necessarias, "status": "Pendente", "seguranca": rules_seguranca
                })
                salvar_dados(ARQUIVO_PLAN, st.session_state.planejamento)
                st.success("Agendado e salvo no arquivo!")
                st.rerun()

# 3. HISTÓRICO DE TROCAS E SERVIÇOS
elif menu == "Histórico de Trocas":
    st.header("📜 Histórico de Manutenções Realizadas e Peças Trocadas")
    
    # Filtro simples por equipamento
    lista_eq_filtro = ["Todos"] + list(set([e['nome'] for e in st.session_state.equipamentos]))
    eq_filtrar = st.selectbox("Filtrar Histórico por Equipamento:", lista_eq_filtro)
    
    for h in st.session_state.historico:
        if eq_filtrar == "Todos" or h['equipamento'] == eq_filtrar:
            st.markdown(f"""
            <div style="padding:12px; border-radius:6px; background-color:#F4FBF7; margin-bottom:8px; border-left:5px solid #28A745; color: black;">
                <b>📅 Data:</b> {h['data']} | <b>⚙️ Máquina:</b> {h['equipamento']} | <b>👷 Executor:</b> {h['executor']}<br>
                📌 <b>Tipo:</b> {h['tipo']} | 📝 <b>Descrição:</b> {h['descricao']}<br>
                🔄 <b>Peças Substituídas de Fato:</b> <span style="color:#D9381E; font-weight:bold;">{h.get('pecas_trocadas', 'Nenhuma')}</span>
            </div>
            """, unsafe_allow_html=True)

# 4. PERMISSÃO DE TRABALHO (PT) COM IMPRESSÃO
elif menu == "Emissão de Permissão de Trabalho (PT)":
    st.header("⚠️ Emissão e Impressão de Permissão de Trabalho (PT)")
    opcoes_pt = {f"{p['id']} - {p['equipamento']} ({p['periodo']})": p for p in st.session_state.planejamento if p['status'] == "Pendente"}
    
    if opcoes_pt:
        selecao = st.selectbox("Selecione a Manutenção Planejada:", list(opcoes_pt.keys()))
        manutencao_selecionada = opcoes_pt[selecao]
        
        colaborador = st.text_input("Nome do Colaborador Executante (Nominal):")
        data_atual = st.date_input("Data de Emissão da PT:")
        pecas_reais = st.text_area("Confirme as Peças Trocadas (para registrar no histórico):", value=manutencao_selecionada['pecas'])
        
        if colaborador:
            # Pega os itens de verificação automáticos daquele período
            itens_verificacao = "<br>".join([f"▢ {i}" for i in CHECKLISTS_PADRAO[manutencao_selecionada['periodo']]])
            
            # Código HTML limpo e estruturado pronto para a impressão limpa do navegador (Ctrl+P)
            documento_html = f"""
            <div id="print-area" style="border: 2px solid #FF4B4B; padding: 25px; border-radius: 8px; background-color: white; color: black; font-family: Arial, sans-serif;">
                <h2 style="text-align: center; color: #FF4B4B; margin-top:0; font-size:24px;">⚠️ PERMISSÃO DE TRABALHO (PT) - Nº 00{manutencao_selecionada['id']}</h2>
                <h4 style="text-align: center; margin:0; color:#555;">Controle de Segurança e Preventiva Industrial</h4>
                <hr style="border: 1px solid #FF4B4B;">
                
                <table style="width:100%; font-size:14px; border-collapse: collapse;">
                    <tr>
                        <td style="padding:5px;"><strong>Colaborador Autorizado (Nominal):</strong> {colaborador}</td>
                        <td style="padding:5px;"><strong>Data de Emissão:</strong> {data_atual.strftime('%d/%m/%Y')}</td>
                    </tr>
                    <tr>
                        <td style="padding:5px;"><strong>Equipamento / Máquina:</strong> {manutencao_selecionada['equipamento']}</td>
                        <td style="padding:5px;"><strong>Tipo de Preventiva:</strong> {manutencao_selecionada['periodo']}</td>
                    </tr>
                </table>
                
                <hr style="border: 0.5px dashed #FF4B4B;">
