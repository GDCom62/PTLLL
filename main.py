import streamlit as st
from datetime import datetime
import base64
import os
import sqlite3

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Controle de Manutenção & PT", layout="wide", page_icon="⚙️")

# --- CONEXÃO E CRIAÇÃO DO BANCO DE DADOS (SQLITE) ---
DB_FILE = "manutencao.db"

def iniciar_banco():
    """Cria as tabelas no banco de dados caso elas não existam"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Tabela de Equipamentos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS equipamentos (
            id TEXT PRIMARY KEY,
            nome TEXT NOT NULL,
            localizacao TEXT,
            criticidade TEXT,
            check_semanal TEXT,
            check_mensal TEXT,
            check_anual TEXT
        )
    """)
    
    # Tabela de Planejamento (Preventivas)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS planejamento (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            equipamento TEXT NOT NULL,
            periodo TEXT,
            data_prevista TEXT,
            pecas TEXT,
            status TEXT DEFAULT 'Pendente',
            seguranca TEXT
        )
    """)
    
    # Insere dados padrão se o banco de dados estiver totalmente vazio
    cursor.execute("SELECT COUNT(*) FROM equipamentos")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO equipamentos VALUES 
            ('EQ-001', 'Torno Mecânico Nardini', 'Oficina Central', 'Alta', 
             'Verificar nível de óleo e lubrificação geral\nLimpeza de resíduos e cavacos\nTestar botão de emergência', 
             'Trocar filtros de óleo\nVerificar tensão de correias', 
             'Revisão do motor elétrico\nSubstituição do fluido hidráulico')
        """)
        cursor.execute("""
            INSERT INTO equipamentos VALUES 
            ('EQ-002', 'Compressor de Ar Schulz', 'Sala de Compressores', 'Média', 
             'Drenar condensado do reservatório\nVerificar ruídos anormais', 
             'Limpar filtro de ar\nVerificar nível de óleo', 
             'Teste hidrostático do vaso\nTroca de válvulas de segurança')
        """)
        cursor.execute("""
            INSERT INTO planejamento (equipamento, periodo, data_prevista, pecas, status, seguranca)
            VALUES ('Torno Mecânico Nardini', 'Semanal', ?, 'Inspeção preventiva padrão', 'Pendente', 'Uso de EPIs obrigatório. Lockout/Tagout.')
        """, (datetime.now().strftime("%d/%m/%Y"),))
        
    conn.commit()
    conn.close()

# Executa a inicialização do arquivo de banco de dados
iniciar_banco()

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
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, localizacao, criticidade FROM equipamentos")
        equipamentos = cursor.fetchall()
        conn.close()
        
        if equipamentos:
            for eq in equipamentos:
                st.write(f"🔹 **[{eq[0]}] {eq[1]}** | Setor: {eq[2]} | Criticidade: {eq[3]}")
                if st.button("🗑️ Remover " + str(eq[0]), key="del_" + str(eq[0])):
                    conn = sqlite3.connect(DB_FILE)
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM equipamentos WHERE id = ?", (eq[0],))
                    conn.commit()
                    conn.close()
                    st.success(f"Equipamento {eq[0]} removido do banco de dados!")
                    st.rerun()
                st.write("---")
        else:
            st.info("Nenhum equipamento cadastrado no banco de dados.")
                        
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
                    conn = sqlite3.connect(DB_FILE)
                    cursor = conn.cursor()
                    try:
                        cursor.execute("INSERT INTO equipamentos VALUES (?, ?, ?, ?, ?, ?, ?)", 
                                       (id_eq, nome_eq, local_eq, crit_eq, c_sem, c_mes, c_ano))
                        conn.commit()
                        st.success("Máquina registrada e salva com sucesso no banco de dados!")
                    except sqlite3.IntegrityError:
                        st.error("Este Código/Tag já está cadastrado!")
                    conn.close()
                else:
                    st.error("Preencha os campos obrigatórios.")

    with aba_editar:
        st.subheader("Editar Máquina Existente")
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, localizacao, criticidade, check_semanal, check_mensal, check_anual FROM equipamentos")
        lista_eq = cursor.fetchall()
        conn.close()
        
        opcoes_edicao = {f"{e[0]} - {e[1]}": e for e in lista_eq}
        if opcoes_edicao:
            selecionado_edicao = st.selectbox("Selecione qual máquina deseja alterar:", list(opcoes_edicao.keys()))
            eq_dados = opcoes_edicao[selecionado_edicao]
            
            with st.form("form_edicao"):
                novo_nome = st.text_input("Nome do Equipamento:", value=eq_dados[1])
                novo_local = st.text_input("Localização / Setor:", value=eq_dados[2])
                novo_crit = st.selectbox("Criticidade:", ["Baixa", "Média", "Alta"], index=["Baixa", "Média", "Alta"].index(eq_dados[3]))
                n_sem = st.text_area("Preventiva Semanal:", value=eq_dados[4])
                n_mes = st.text_area("Preventiva Mensal:", value=eq_dados[5])
                n_ano = st.text_area("Preventiva Anual:", value=eq_dados[6])
                
                if st.form_submit_button("Gravar Alterações"):
                    conn = sqlite3.connect(DB_FILE)
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE equipamentos 
                        SET nome=?, localizacao=?, criticidade=?, check_semanal=?, check_mensal=?, check_anual=?
                        WHERE id=?
                    """, (novo_nome, novo_local, novo_crit, n_sem, n_mes, n_ano, eq_dados[0]))
                    conn.commit()
                    conn.close()
                    st.success("Alterações gravadas no arquivo de banco de dados!")
                    st.rerun()
        else:
            st.info("Nenhum equipamento cadastrado para edição.")

# ==========================================
# 2. PÁGINA: PLANEJAMENTO TEMPORAL
# ==========================================
elif menu == "📅 Planejamento & Checklists":
    st.header("📅 Planejamento de Manutenções Preventivas")
    aba_sem, aba_mes, aba_ano, aba_novo = st.tabs(["🗓️ Semanal", "📅 Mensal", "⏳ Anual", "➕ Agendar Preventiva"])
    
    # Busca planejamentos pendentes direto da API do Supabase com rota limpa
    req_plan = requests.get(f"{SUB_URL}/rest/v1/planejamento?status=eq.Pendente&select=*&order=id.asc", headers=SUB_HEADERS)
    todos_agendamentos = req_plan.json() if req_plan.status_code == 200 else []

    def renderizar_lista_preventivas(dados_filtrados):
        if dados_filtrados and isinstance(dados_filtrados, list):
            for p in dados_filtrados:
                col_dados, col_acao = st.columns([4, 1])
                with col_dados:
                    st.write("⚙️ **" + str(p['equipamento']) + "** | 📅 **Data Prevista:** " + str(p.get('data_prevista')) + " | **Status:** " + str(p['status']))
                    st.write("🔧 Peças Programadas: " + str(p['pecas']))
                with col_acao:
                    if st.button("✔️ Concluir", key="comp_" + str(p['id'])):
                        # Insere o registro finalizado na tabela de historico via API
                        registro_historico = {
                            "equipamento": p['equipamento'],
                            "periodo": p['periodo'],
                            "data_prevista": p['data_prevista'],
                            "data_conclusao": datetime.now().strftime("%d/%m/%Y %H:%M"),
                            "pecas": p['pecas'],
                            "status": "Concluído"
                        }
                        requests.post(f"{SUB_URL}/rest/v1/historico", json=registro_historico, headers=SUB_HEADERS)
                        
                        # Deleta a ordem pendente antiga via API
                        requests.delete(f"{SUB_URL}/rest/v1/planejamento?id=eq.{p['id']}", headers=SUB_HEADERS)
                        
                        st.success("Ordem de serviço finalizada e salva permanentemente no histórico!")
                        st.rerun()
                st.write("---")
        else:
            st.info("Nenhuma manutenção preventiva pendente para este período.")

    with aba_sem:
        if isinstance(todos_agendamentos, list):
            renderizar_lista_preventivas([a for a in todos_agendamentos if a.get('periodo') == "Semanal"])

    with aba_mes:
        if isinstance(todos_agendamentos, list):
            renderizar_lista_preventivas([a for a in todos_agendamentos if a.get('periodo') == "Mensal"])

    with aba_ano:
        if isinstance(todos_agendamentos, list):
            renderizar_lista_preventivas([a for a in todos_agendamentos if a.get('periodo') == "Anual"])
    
    with aba_novo:
        st.subheader("📋 Agendar Nova Preventiva")
        # Busca as máquinas da API para o seletor
        req_eq = requests.get(f"{SUB_URL}/rest/v1/equipamentos?select=nome&order=nome.asc", headers=SUB_HEADERS)
        eq_data = req_eq.json() if req_eq.status_code == 200 else []
        lista_nomes = [row['nome'] for row in eq_data] if isinstance(eq_data, list) else []
        opcoes_selecao = lista_nomes if lista_nomes else ["Nenhum equipamento cadastrado"]
        
        with st.form("form_novo_planejamento"):
            eq_escolhido = st.selectbox("Selecione a Máquina Alvo:", opcoes_selecao)
            periodo_escolhido = st.selectbox("Escolha o Período:", ["Semanal", "Mensal", "Anual"])
            data_planejada = st.date_input("Selecione a Data do Serviço:", datetime.now())
            pecas_necessarias = st.text_area("Descrição das Peças / Notas adicionais:", value="Inspeção preventiva padrão")
            
            if st.form_submit_button("Agendar Manutenção"):
                if eq_escolhido != "Nenhum equipamento cadastrado":
                    novo_agendamento = {
                        "equipamento": eq_escolhido,
                        "periodo": periodo_escolhido,
                        "data_prevista": data_planejada.strftime("%d/%m/%Y"),
                        "pecas": pecas_necessarias,
                        "status": "Pendente",
                        "seguranca": "Uso de EPIs obrigatório. Verificar bloqueios elétricos."
                    }
                    res_plan = requests.post(f"{SUB_URL}/rest/v1/planejamento", json=novo_agendamento, headers=SUB_HEADERS)
                    if res_plan.status_code < 400:
                        st.success("Manutenção agendada e guardada com sucesso na nuvem permanentemente!")
                        st.rerun()
                    else:
                        st.error(f"Erro ao agendar manutenção no banco: {res_plan.text}")

# ==========================================
# 3. PÁGINA: HISTÓRICO DE TROCAS
# ==========================================
elif menu == "📜 Histórico de Trocas":
    st.header("📜 Histórico de Trocas e Manutenções Concluídas")
    # Busca os históricos finalizados na API
    req_hist = requests.get(f"{SUB_URL}/rest/v1/historico?select=*&order=id.desc", headers=SUB_HEADERS)
    historico_lista = req_hist.json() if req_hist.status_code == 200 else []
    
    if historico_lista and isinstance(historico_lista, list):
        for h in list(historico_lista):
            st.write("✅ **" + str(h['equipamento']) + "** | Período: " + str(h['periodo']))
            st.write("📅 **Planejado para:** " + str(h['data_prevista']) + " | ⏱️ **Encerrado em:** " + str(h.get('data_conclusao', 'N/A')))
            st.write("🔧 Peças / Intervenções: " + str(h['pecas']))
            st.write("---")
    else:
        st.info("Nenhuma ordem de serviço foi finalizada no sistema ainda.")

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

    # Busca ordens ativas para gerar a PT
    req_pend = requests.get(f"{SUB_URL}/rest/v1/planejamento?status=eq.Pendente&select=*&order=id.asc", headers=SUB_HEADERS)
    ordens_pendentes = req_pend.json() if req_pend.status_code == 200 else []
    
    if not ordens_pendentes or not isinstance(ordens_pendentes, list):
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
                    id_print = "pt_print_" + str(os_dados['id'])

                else:
                    id_print = "pt_print_" + str(os_dados['id'])
