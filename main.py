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
                    st.success("Alterações salvas com sucesso!")
                    st.rerun()
# ==========================================
# 2. PÁGINA: PLANEJAMENTO TEMPORAL
# ==========================================
elif menu == "📅 Planejamento & Checklists":
    st.header("📅 Planejamento de Manutenções Preventivas")
    aba_sem, aba_mes, aba_ano, aba_novo = st.tabs(["🗓️ Semanal", "📅 Mensal", "⏳ Anual", "➕ Agendar Preventiva"])
    
    with aba_sem:
        dados_sem = [p for p in st.session_state.planejamento if p['periodo'] == "Semanal" and p['status'] == "Pendente"]
        if dados_sem:
            for p in dados_sem:
                st.write("⚙️ **" + str(p['equipamento']) + "** | 📅 **Data:** " + str(p.get('data_prevista')) + " | **Status:** " + str(p['status']))
                st.write("🔧 Peças Programadas: " + str(p['pecas']))
                st.write("---")
        else:
            st.info("Nenhuma preventiva semanal pendente.")

    with aba_mes:
        dados_mes = [p for p in st.session_state.planejamento if p['periodo'] == "Mensal" and p['status'] == "Pendente"]
        if dados_mes:
            for p in dados_mes:
                st.write("⚙️ **" + str(p['equipamento']) + "** | 📅 **Data:** " + str(p.get('data_prevista')) + " | **Status:** " + str(p['status']))
                st.write("🔧 Peças Programadas: " + str(p['pecas']))
                st.write("---")
        else:
            st.info("Nenhuma preventiva mensal pendente.")

    with aba_ano:
        dados_ano = [p for p in st.session_state.planejamento if p['periodo'] == "Anual" and p['status'] == "Pendente"]
        if dados_ano:
            for p in dados_ano:
                st.write("⚙️ **" + str(p['equipamento']) + "** | 📅 **Data:** " + str(p.get('data_prevista')) + " | **Status:** " + str(p['status']))
                st.write("🔧 Peças Programadas: " + str(p['pecas']))
                st.write("---")
        else:
            st.info("Nenhuma preventiva anual pendente.")
    
    with aba_novo:
        st.subheader("📋 Agendar Nova Preventiva")
        lista_nomes = [e['nome'] for e in st.session_state.equipamentos]
        opcoes_selecao = lista_nomes if lista_nomes else ["Nenhum equipamento cadastrado"]
        
        with st.form("form_novo_planejamento"):
            eq_escolhido = st.selectbox("Selecione a Máquina Alvo:", opcoes_selecao)
            periodo_escolhido = st.selectbox("Escolha o Período:", ["Semanal", "Mensal", "Anual"])
            data_planejada = st.date_input("Selecione a Data do Serviço:", datetime.now())
            pecas_necessarias = st.text_area("Descrição das Peças / Notas adicionais:", value="Inspeção preventiva padrão")
            
            if st.form_submit_button("Agendar Manutenção"):
                if eq_escolhido != "Nenhum equipamento cadastrado":
                    novo_id = len(st.session_state.planejamento) + 1
                    st.session_state.planejamento.append({
                        "id": novo_id,
                        "equipamento": eq_escolhido,
                        "periodo": periodo_escolhido,
                        "data_prevista": data_planejada.strftime("%d/%m/%Y"),
                        "pecas": pecas_necessarias,
                        "status": "Pendente",
                        "seguranca": "Uso de EPIs obrigatório. Verificar bloqueios elétricos."
                    })
                    if "pt_gerada_html" in st.session_state:
                        st.session_state.pt_gerada_html = None
                    st.success("Manutenção agendada com sucesso!")
                    st.rerun()

# ==========================================
# 3. PÁGINA: HISTÓRICO DE TROCAS
# ==========================================
elif menu == "📜 Histórico de Trocas":
    st.header("📜 Histórico de Trocas e Manutenções Concluídas")
    st.info("Esta seção exibirá o histórico de ordens finalizadas da fábrica.")

# ==========================================
# 4. PÁGINA: EMISSÃO DE PT
# ==========================================
elif menu == "⚠️ Emissão de PT":
    st.header("⚠️ Emissão e Impressão de Permissão de Trabalho (PT)")
    
    if "pt_gerada_html" not in st.session_state:
        st.session_state.pt_gerada_html = None
    if "pt_gerada_txt" not in st.session_state:
        st.session_state.pt_gerada_txt = None
    if "pt_id_atual" not in st.session_state:
        st.session_state.pt_id_atual = None

    ordens_pendentes = [p for p in st.session_state.planejamento if p['status'] == "Pendente"]
    
    if not ordens_pendentes:
        st.warning("Não existem manutenções pendentes no momento para emitir uma PT. Agende uma preventiva primeiro!")
    else:
        opcoes_os = {f"OS #{p['id']} - {p['equipamento']} ({p['periodo']})": p for p in ordens_pendentes}
        os_selecionada_str = str(st.selectbox("Selecione a Ordem de Serviço para vincular à PT:", list(opcoes_os.keys())))
        os_dados = opcoes_os[os_selecionada_str]
        
        if st.session_state.pt_id_atual != os_dados['id']:
            st.session_state.pt_gerada_html = None
            st.session_state.pt_gerada_txt = None
            st.session_state.pt_id_atual = os_dados['id']
        
        st.markdown("---")
        st.subheader("📋 Formulário de Liberação de Segurança")
        
        with st.form("form_emissao_pt"):
            col1, col2 = st.columns(2)
            
            with col1:
                emitente = st.text_input("Nome do Emitente / Supervisor:", value="Supervisor de Manutenção")
                executante = st.text_input("Nome do Executante / Técnico:")
                empresa_exec = st.selectbox("Empresa Executante:", ["Própria (Interna)", "Terceirizada / Contratada"])
            
            with col2:
                validade_data = st.date_input("Válido para o dia:", datetime.now())
                hora_inicio = st.time_input("Horário de Início Autorizado:", value=datetime.strptime("08:00", "%H:%M").time())
                hora_fim = st.time_input("Horário de Término Máximo:", value=datetime.strptime("17:00", "%H:%M").time())
            
            st.markdown("##### 🚨 Análise de Riscos e Riscos Envolvidos")
            col_r1, col_r2, col_r3 = st.columns(3)
            with col_r1:
                r_altura = st.checkbox("Trabalho em Altura (NR-35)")
                r_eletrico = st.checkbox("Risco Elétrico / Energias Vivas (NR-10)")
            with col_r2:
                r_confinado = st.checkbox("Espaço Confinado (NR-33)")
                r_quimico = st.checkbox("Risco Químico (Gases/Vapores/Ácidos)")
            with col_r3:
                r_quente = st.checkbox("Trabalho a Quente (Solda/Esmeril/Corte)")
                r_mecanico = st.checkbox("Risco Mecânico (Prensamento/Corte)")
                
            st.markdown("##### 🛡️ Medidas de Controle Obrigatórias")
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                c_loto = st.checkbox("Bloqueio e Etiquetagem executados (LOTO / Lockout Tagout)", value=True)
                c_delim = st.checkbox("Área devidamente isolada e sinalizada", value=True)
            with col_c2:
                c_epi = st.checkbox("EPIs básicos e específicos verificados", value=True)
                c_extintor = st.checkbox("Equipamento de combate a incêndio posicionado no local")

            observacoes_seg = st.text_area("Observações Adicionais de Segurança:", value=str(os_dados.get('seguranca', '')))
            
            bt_gerar = st.form_submit_button("Validar e Gerar Documento de PT")
            
            if bt_gerar:
                if not executante:
                    st.error("Por favor, preencha o nome do técnico executante para assinar a ordem.")
                else:
                    id_impressao = f"pt_print_{os_dados['id']}"
                    
                    st.session_state.pt_gerada_html = f"""
                    <div id="{id_impressao}" style="border: 3px double #FF0000; padding: 20px; background-color: #FFF5F5; color: #000000; font-family: monospace; border-radius: 5px; margin-bottom: 20px;">
                        <h2 style="text-align: center; color: #FF0000; margin-bottom: 20px;">⚠️ PERMISSÃO DE TRABALHO (PT) - REGISTRO INDUSTRIAL</h2>
                        <p><b>CÓDIGO PT:</b> PT-{os_dados['id']}{datetime.now().strftime('%M%S')} | <b>VINCULADO À:</b> OS #{os_dados['id']}</p>
                        <p><b>EQUIPAMENTO:</b> {os_dados['equipamento']} | <b>SERVIÇO:</b> {os_dados['pecas']}</p>
                        <hr style='border-top: 1px dashed #FF0000;'>
                        <p><b>EMITENTE/SUPERVISOR:</b> {emitente} | <b>EXECUTANTE:</b> {executante} ({empresa_exec})</p>
                        <p><b>VALIDADE:</b> {validade_data.strftime('%d/%m/%Y')} das {hora_inicio.strftime('%H:%M')} às {hora_fim.strftime('%H:%M')}</p>
                        <hr style='border-top: 1px dashed #FF0000;'>
                        <p><b>RISCOS DETECTADOS:</b><br>
                        {"- Trabalho em Altura<br>" if r_altura else ""}
                        {"- Risco Elétrico<br>" if r_eletrico else ""}
                        {"- Espaço Confinado<br>" if r_confinado else ""}
                        {"- Risco Químico<br>" if r_quimico else ""}
                        {"- Trabalho a Quente<br>" if r_quente else ""}
                        {"- Risco Mecânico<br>" if r_mecanico else ""}
                        </p>
                        <p><b>CONTROLES EXECUTADOS:</b><br>
                        {"[X] Lockout / Tagout Ativo<br>" if c_loto else ""}
                        {"[X] Área Isolada<br>" if c_delim else ""}
                        {"[X] EPIs Verificados<br>" if c_epi else ""}
                        {"[X] Proteção Incêndio Pronta<br>" if c_extintor else ""}
                        </p>
                        <p><b>OBSERVAÇÕES:</b> {observacoes_seg}</p>
                        <br><br>
