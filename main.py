import streamlit as st
from datetime import datetime
import pandas as pd
import requests

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Controle de Manutenção & PT", layout="wide", page_icon="⚙️")

# --- CONEXÃO COM O SUPABASE VIA REST API ---
def obter_credenciais():
    try:
        url = st.secrets["supabase"]["url"].strip().rstrip("/")
        key = st.secrets["supabase"]["key"].strip()
        return url, key
    except Exception as e:
        st.error(f"Erro ao ler os Secrets no Streamlit: {e}")
        return None, None

SUBAPASE_URL, SUPABASE_KEY = obter_credenciais()

# --- FUNÇÕES DE BANCO DE DADOS DIRETO ---
def buscar_dados(tabela: str):
    if not SUBAPASE_URL or not SUPABASE_KEY:
        return []
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    url = f"{SUBAPASE_URL}/rest/v1/{tabela}?select=*"
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return []

def inserir_dados(tabela: str, payload: dict):
    if not SUBAPASE_URL or not SUPABASE_KEY:
        return False
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    url = f"{SUBAPASE_URL}/rest/v1/{tabela}"
    try:
        response = requests.post(url, headers=headers, json=payload)
        return 200 <= response.status_code <= 299
    except Exception:
        return False

def atualizar_dados(tabela: str, payload: dict, coluna_id: str, valor_id):
    if not SUBAPASE_URL or not SUPABASE_KEY:
        return False
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    url = f"{SUBAPASE_URL}/rest/v1/{tabela}?{coluna_id}=eq.{valor_id}"
    try:
        response = requests.patch(url, headers=headers, json=payload)
        return 200 <= response.status_code <= 299
    except Exception:
        return False

def excluir_dados(tabela: str, coluna_id: str, valor_id):
    if not SUBAPASE_URL or not SUPABASE_KEY:
        return False
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    url = f"{SUBAPASE_URL}/rest/v1/{tabela}?{coluna_id}=eq.{valor_id}"
    try:
        response = requests.delete(url, headers=headers)
        return 200 <= response.status_code <= 299
    except Exception:
        return False

# Estados de controle para edição ativa
if "editando_maquina_id" not in st.session_state:
    st.session_state.editando_maquina_id = None
if "editando_os_id" not in st.session_state:
    st.session_state.editando_os_id = None

# --- MENU LATERAL DE NAVEGAÇÃO ---
# Carrega o logo principal local da árvore do GitHub (pequeno no topo)
try:
    st.sidebar.image("logo.png", width=120)
except Exception:
    pass

st.sidebar.title("⚙️ Gestão de Manutenção")
menu = st.sidebar.radio("Navegar para:", [
    "🔍 Abas 1 & 2: Gerenciar Máquinas",
    "📅 Aba 3: Ordens de Serviço (OS)",
    "📜 Aba 4: Histórico de Trocas",
    "⚠️ Aba 5: Emissão de PT"
])

# Carregamento de dados dinâmico e integrado ao vivo
equipamentos = buscar_dados("maquinas")
todos_agendamentos = buscar_dados("planejamento")
historico_lista = buscar_dados("historico")

# ==========================================
# ABAS 1 & 2: GERENCIAR MÁQUINAS
# ==========================================
if menu == "🔍 Abas 1 & 2: Gerenciar Máquinas":
    st.header("🔍 Gerenciamento de Equipamentos")
    
    if st.session_state.editando_maquina_id is not None:
        st.subheader("✏️ Editar Equipamento Registrado")
        mq_editar = next((m for m in equipamentos if str(m["id"]) == str(st.session_state.editando_maquina_id)), None)
        
        if mq_editar:
            with st.form("form_editar_maquina"):
                st.info(f"Editando Tag: {mq_editar.get('id')}")
                edit_nome = st.text_input("Nome do Equipamento:", value=mq_editar.get("nome", ""))
                edit_local = st.text_input("Localização / Setor:", value=mq_editar.get("localizacao", ""))
                edit_crit = st.selectbox("Criticidade:", ["Baixa", "Média", "Alta"], index=["Baixa", "Média", "Alta"].index(mq_editar.get("criticidade", "Baixa")) if mq_editar.get("criticidade") in ["Baixa", "Média", "Alta"] else 0)
                edit_sem = st.text_area("Checklist Semanal:", value=mq_editar.get("check_semanal", ""))
                edit_mes = st.text_area("Checklist Mensal:", value=mq_editar.get("check_mensal", ""))
                edit_ano = st.text_area("Checklist Anual:", value=mq_editar.get("check_anual", ""))
                btn_salvar_mq = st.form_submit_button("💾 Salvar Alterações")
                
            if btn_salvar_mq:
                payload = {"nome": edit_nome, "localizacao": edit_local, "criticidade": edit_crit, "check_semanal": edit_sem, "check_mensal": edit_mes, "check_anual": edit_ano}
                if atualizar_dados("maquinas", payload, "id", mq_editar["id"]):
                    st.success("🎉 Equipamento atualizado com sucesso no Supabase!")
                    st.session_state.editando_maquina_id = None
                    st.rerun()
                else:
                    st.error("Erro ao salvar atualizações.")
            
            if st.button("❌ Cancelar Edição"):
                st.session_state.editando_maquina_id = None
                st.rerun()
    else:
        st.subheader("➕ Cadastrar Nova Máquina")
        with st.form("form_cadastro_direto"):
            id_eq = st.text_input("Tag do Equipamento (Ex: EQ-003):").strip()
            nome_eq = st.text_input("Nome do Equipamento:").strip()
            local_eq = st.text_input("Localização / Setor:")
            crit_eq = st.selectbox("Criticidade:", ["Baixa", "Média", "Alta"])
            st.markdown("##### 📜 Ações Preventivas")
            c_sem = st.text_area("Checklist Semanal:", "1. Verificar nível de óleo; 2. Limpeza.")
            c_mes = st.text_area("Checklist Mensal:", "1. Troca de filtros.")
            c_ano = st.text_area("Checklist Anual:", "1. Revisão preventiva.")
            botao_salvar = st.form_submit_button("Salvar Novo Equipamento")
            
        if botao_salvar and id_eq and nome_eq:
            payload = {"id": id_eq, "nome": nome_eq, "localizacao": local_eq, "criticidade": crit_eq, "check_semanal": c_sem, "check_mensal": c_mes, "check_anual": c_ano}
            if inserir_dados("maquinas", payload):
                st.success("🎉 Equipamento salvo diretamente no Supabase!")
                st.rerun()
            else:
                st.error("Erro ao inserir equipamento no banco de dados.")

    st.markdown("---")
    st.subheader("📋 Lista de Equipamentos Registrados")
    if not equipamentos:
        st.info("Nenhuma máquina encontrada na tabela 'maquinas' do Supabase.")
    else:
        for mq in equipamentos:
            st.write(f"🔹 **[{mq.get('id')}] {mq.get('nome')}** | Setor: {mq.get('localizacao')} | Criticidade: {mq.get('criticidade')}")
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                if st.button(f"✏️ Editar {mq.get('id')}", key=f"ed_mq_{mq.get('id')}"):
                    st.session_state.editando_maquina_id = mq.get('id')
                    st.rerun()
            with col_m2:
                if st.button(f"🗑️ Excluir {mq.get('id')}", key=f"ex_mq_{mq.get('id')}"):
                    if excluir_dados("maquinas", "id", mq.get('id')):
                        st.warning("Equipamento excluído permanentemente do Supabase!")
                        st.rerun()
            st.write("---")

# ==========================================
# ABA 3: PLANEJAMENTO E ORDENS DE SERVIÇO (OS)
# ==========================================
elif menu == "📅 Aba 3: Ordens de Serviço (OS)":
    st.header("📅 Planejamento & Ordens de Serviço (OS)")
    
    if st.session_state.editando_os_id is not None:
        st.subheader("📝 Editar Ordem de Serviço Ativa")
        os_editar = next((item for item in todos_agendamentos if str(item["id"]) == str(st.session_state.editando_os_id)), None)
        
        if os_editar:
            with st.form("form_editar_os"):
                edit_equip = st.selectbox("Máquina Alvo:", [m["nome"] for m in equipamentos] if equipamentos else ["Nenhuma cadastrada"])
                edit_periodo = st.selectbox("Escolha o Período:", ["Semanal", "Mensal", "Anual"])
                edit_data = st.date_input("Data Prevista:", datetime.now())
                edit_pecas = st.text_area("Escopo do Serviço:", value=os_editar.get("pecas", ""))
                edit_seg = st.text_area("Observações de Segurança:", value=os_editar.get("seguranca", ""))
                btn_salvar_os = st.form_submit_button("💾 Salvar Alterações da OS")
                
            if btn_salvar_os:
                payload = {"equipamento": edit_equip, "periodo": edit_periodo, "data_prevista": edit_data.strftime("%d/%m/%Y"), "pecas": edit_pecas, "seguranca": edit_seg}
                if atualizar_dados("planejamento", payload, "id", os_editar["id"]):
                    st.success("🎉 Alterações na OS gravadas com sucesso!")
                    st.session_state.editando_os_id = None
                    st.rerun()
            
            if st.button("❌ Cancelar Edição da OS"):
                st.session_state.editando_os_id = None
                st.rerun()
    else:
        st.subheader("📅 Agendar Nova Manutenção / Gerar OS")
        with st.form("form_agenda_direto"):
            lista_nomes = [m["nome"] for m in equipamentos]
            eq_escolhido = st.selectbox("Selecione a Máquina Alvo:", lista_nomes if lista_nomes else ["Nenhum cadastrado"])
            periodo_escolhido = st.selectbox("Escolha o Período:", ["Semanal", "Mensal", "Anual"])
            data_planejada = st.date_input("Selecione a Data:", datetime.now())
            pecas_necessarias = st.text_area("Descrição das Peças / Escopo:", value="Realizar rotina padrão de preventiva.")
            seg_necessaria = st.text_area("Observações Iniciais de Segurança:", value="Seguir as NRs de segurança aplicadas.")
            botao_agenda = st.form_submit_button("💾 Gerar OS Pendente")
            
        if botao_agenda and eq_escolhido != "Nenhum cadastrado":
            payload = {"equipamento": eq_escolhido, "periodo": periodo_escolhido, "data_prevista": data_planejada.strftime("%d/%m/%Y"), "pecas": pecas_necessarias, "status": "Pendente", "seguranca": seg_necessaria}
            if inserir_dados("planejamento", payload):
                st.success("🎉 Ordem de Serviço OS inserida e gravada com sucesso!")
                st.rerun()
# ==========================================
# ABA 4: HISTÓRICO DE TROCAS & GRÁFICOS
# ==========================================
elif menu == "📜 Aba 4: Histórico de Trocas":
    st.header("📜 Histórico de Manutenções Fechadas")
    
    if not historico_lista:
        st.info("Nenhum registro de fechamento encontrado na tabela 'historico' do Supabase.")
    else:
        # Converter a lista de dicionários do banco em um DataFrame para análise de dados
        df_hist = pd.DataFrame(historico_lista)
        
        st.subheader("📊 Gráficos de Atendimento Industrial")
        col_g1, col_g2 = st.columns(2)
        
        with col_g1:
            st.markdown("##### 📅 Evolução Mensal de Serviços")
            # Extrai o mês e o ano da data de conclusão (Formato esperado: DD/MM/AAAA)
            try:
                df_hist['Mes_Ano'] = df_hist['data_conclusao'].apply(lambda x: str(x).split()[0][3:10] if len(str(x)) >= 10 else "Sem Data")
                dados_mensal = df_hist['Mes_Ano'].value_counts().reset_index()
                dados_mensal.columns = ['Mês/Ano', 'Total de Atendimentos']
                st.bar_chart(dados_mensal.set_index('Mês/Ano'))
            except Exception:
                st.caption("Aguardando mais dados formatados para gerar a evolução mensal.")
                
        with col_g2:
            st.markdown("##### 📆 Evolução Anual de Serviços")
            try:
                df_hist['Ano'] = df_hist['data_conclusao'].apply(lambda x: str(x).split()[0][6:10] if len(str(x)) >= 10 else "Sem Ano")
                dados_anual = df_hist['Ano'].value_counts().reset_index()
                dados_anual.columns = ['Ano', 'Total de Atendimentos']
                st.bar_chart(dados_anual.set_index('Ano'))
            except Exception:
                st.caption("Aguardando mais dados formatados para gerar a evolução anual.")

        st.markdown("---")
        st.subheader("📋 Listagem Completa de Ordens Concluídas")
        
        # Exibe os dados do histórico de forma limpa na tela
        for h in historico_lista:
            st.write(f"✅ **{h.get('equipamento', 'Equipamento')}** | Frequência: **{str(h.get('periodo', 'N/A')).upper()}**")
            st.write(f"⏱️ **Concluído em:** {h.get('data_conclusao', 'N/A')} | **Serviço executado:** {h.get('pecas', 'N/A')}")
            st.write("---")

# ==========================================
# ABA 5: EMISSÃO DE PERMISSÃO DE TRABALHO (PT)
# ==========================================
elif menu == "⚠️ Aba 5: Emissão de PT":
    st.header("⚠️ Emissão e Impressão de Permissão de Trabalho (PT)")
    
    # Filtra apenas as ordens que estão abertas (Pendentes) para vincular à PT
    ordens_pendentes = [p for p in todos_agendamentos if p.get('status') == "Pendente"]
    
    if not ordens_pendentes:
        st.warning("Não existem manutenções abertas no Supabase no momento para emitir uma PT.")
    else:
        opcoes_os = {f"OS #{p['id']} - {p['equipamento']} ({p.get('periodo')})": p for p in ordens_pendentes}
        os_selecionada_str = str(st.selectbox("Selecione a Ordem de Serviço para vincular à PT:", list(opcoes_os.keys())))
        os_dados = opcoes_os[os_selecionada_str]
        
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
            
            st.markdown("##### 🚨 Análise de Riscos Envolvidos")
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
                st.success("✅ Permissão de Trabalho gerada com sucesso na memória do sistema!")
                
                # CSS Customizado Industrial para emoldurar o documento para impressão
                st.markdown("""
                <style>
                    .pt-box { border: 3px double #FF0000; padding: 20px; background-color: #FFF5F5; color: #000000; font-family: monospace; border-radius: 5px; }
                    .pt-title { text-align: center; color: #FF0000; margin-bottom: 20px; }
                </style>
                """, unsafe_html=True)
                
                conteudo_pt = f"""
                <div class="pt-box">
                    <h2 class="pt-title">⚠️ PERMISSÃO DE TRABALHO (PT) - REGISTRO INDUSTRIAL</h2>
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
                    <p style='text-align: center;'>________________________________________<br>Assinatura Digital do Supervisor (Liberado)</p>
                </div>
                """
                st.markdown(conteudo_pt, unsafe_html=True)
                
                # Botão nativo para baixar a cópia limpa do texto pronta para enviar para a impressora
                st.download_button(
                    label="🖨️ Baixar Cópia do Texto para Impressão",
                    data=conteudo_pt.replace("<br>", "\n").replace("<p>", "").replace("</p>", "\n").replace("<div>", "").replace("</div>", "").replace("<b>", "").replace("</b>", "").replace("<hr style='border-top: 1px dashed #FF0000;'>", "-----------------------"),
                    file_name=f"Permissao_Trabalho_OS_{os_dados['id']}.txt",
                    mime="text/plain",
                    use_container_width=True
                )

# ==========================================
# ABA 4: HISTÓRICO DE TROCAS & GRÁFICOS
# ==========================================
elif menu == "📜 Aba 4: Histórico de Trocas":
    st.header("📜 Histórico de Manutenções Fechadas")
    
    if not historico_lista:
        st.info("Nenhum registro de fechamento encontrado na tabela 'historico' do Supabase.")
    else:
        # Converter a lista de dicionários do banco em um DataFrame para análise de dados
        df_hist = pd.DataFrame(historico_lista)
        
        st.subheader("📊 Gráficos de Atendimento Industrial")
        col_g1, col_g2 = st.columns(2)
        
        with col_g1:
            st.markdown("##### 📅 Evolução Mensal de Serviços")
            # Extrai o mês e o ano da data de conclusão (Formato esperado: DD/MM/AAAA)
            try:
                df_hist['Mes_Ano'] = df_hist['data_conclusao'].apply(lambda x: str(x).split()[0][3:10] if len(str(x)) >= 10 else "Sem Data")
                dados_mensal = df_hist['Mes_Ano'].value_counts().reset_index()
                dados_mensal.columns = ['Mês/Ano', 'Total de Atendimentos']
                st.bar_chart(dados_mensal.set_index('Mês/Ano'))
            except Exception:
                st.caption("Aguardando mais dados formatados para gerar a evolução mensal.")
                
        with col_g2:
            st.markdown("##### 📆 Evolução Anual de Serviços")
            try:
                df_hist['Ano'] = df_hist['data_conclusao'].apply(lambda x: str(x).split()[0][6:10] if len(str(x)) >= 10 else "Sem Ano")
                dados_anual = df_hist['Ano'].value_counts().reset_index()
                dados_anual.columns = ['Ano', 'Total de Atendimentos']
                st.bar_chart(dados_anual.set_index('Ano'))
            except Exception:
                st.caption("Aguardando mais dados formatados para gerar a evolução anual.")

        st.markdown("---")
        st.subheader("📋 Listagem Completa de Ordens Concluídas")
        
        # Exibe os dados do histórico de forma limpa na tela
        for h in historico_lista:
            st.write(f"✅ **{h.get('equipamento', 'Equipamento')}** | Frequência: **{str(h.get('periodo', 'N/A')).upper()}**")
            st.write(f"⏱️ **Concluído em:** {h.get('data_conclusao', 'N/A')} | **Serviço executado:** {h.get('pecas', 'N/A')}")
            st.write("---")

# ==========================================
# ABA 5: EMISSÃO DE PERMISSÃO DE TRABALHO (PT)
# ==========================================
elif menu == "⚠️ Aba 5: Emissão de PT":
    st.header("⚠️ Emissão e Impressão de Permissão de Trabalho (PT)")
    
    # Filtra apenas as ordens que estão abertas (Pendentes) para vincular à PT
    ordens_pendentes = [p for p in todos_agendamentos if p.get('status') == "Pendente"]
    
    if not ordens_pendentes:
        st.warning("Não existem manutenções abertas no Supabase no momento para emitir uma PT.")
    else:
        opcoes_os = {f"OS #{p['id']} - {p['equipamento']} ({p.get('periodo')})": p for p in ordens_pendentes}
        os_selecionada_str = str(st.selectbox("Selecione a Ordem de Serviço para vincular à PT:", list(opcoes_os.keys())))
        os_dados = opcoes_os[os_selecionada_str]
        
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
            
            st.markdown("##### 🚨 Análise de Riscos Envolvidos")
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
                st.success("✅ Permissão de Trabalho gerada com sucesso na memória do sistema!")
                
                # CSS Customizado Industrial para emoldurar o documento para impressão
                st.markdown("""
                <style>
                    .pt-box { border: 3px double #FF0000; padding: 20px; background-color: #FFF5F5; color: #000000; font-family: monospace; border-radius: 5px; }
                    .pt-title { text-align: center; color: #FF0000; margin-bottom: 20px; }
                </style>
                """, unsafe_html=True)
                
                conteudo_pt = f"""
                <div class="pt-box">
                    <h2 class="pt-title">⚠️ PERMISSÃO DE TRABALHO (PT) - REGISTRO INDUSTRIAL</h2>
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
                    <p style='text-align: center;'>________________________________________<br>Assinatura Digital do Supervisor (Liberado)</p>
                </div>
                """
                st.markdown(conteudo_pt, unsafe_html=True)
                
                # Botão nativo para baixar a cópia limpa do texto pronta para enviar para a impressora
                st.download_button(
                    label="🖨️ Baixar Cópia do Texto para Impressão",
                    data=conteudo_pt.replace("<br>", "\n").replace("<p>", "").replace("</p>", "\n").replace("<div>", "").replace("</div>", "").replace("<b>", "").replace("</b>", "").replace("<hr style='border-top: 1px dashed #FF0000;'>", "-----------------------"),
                    file_name=f"Permissao_Trabalho_OS_{os_dados['id']}.txt",
                    mime="text/plain",
                    use_container_width=True
                )

if __name__ == "__main__":
    pass
# --- RODAPÉ DISCRETO DO DESENVOLVEDOR (Fixo no canto inferior direito) ---
st.markdown("""
    <style>
        .footer-dev {
            position: fixed;
            bottom: 10px;
            right: 20px;
            display: flex;
            align-items: center;
            gap: 8px;
            background-color: transparent;
            z-index: 999;
        }
        .footer-dev img {
            width: 22px;
            height: auto;
        }
        .footer-dev span {
            font-size: 11px;
            color: #888888;
            font-family: sans-serif;
        }
    </style>
""", unsafe_html=True)

# Injeta a marca GDCOM com o arquivo logdcom1.png local de forma flutuante e profissional
try:
    with open("logdcom1.png", "rb") as f:
        import base64
        data_logdcom = base64.b64encode(f.read()).decode("utf-8")
    
    st.markdown(f"""
        <div class="footer-dev">
            <span>Desenvolvido por GDCOM</span>
            <img src="data:image/png;base64,{data_logdcom}">
        </div>
    """, unsafe_html=True)
except Exception:
    # Caso o arquivo mude de nome por acidente, mantém apenas o texto limpo para não travar
    st.markdown("""
        <div class="footer-dev">
            <span>Desenvolvido por GDCOM</span>
        </div>
    """, unsafe_html=True)
