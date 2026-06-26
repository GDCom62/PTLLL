import streamlit as st
from datetime import datetime
import base64
import os
from supabase import create_client, Client

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Controle de Manutenção & PT", layout="wide", page_icon="⚙️")

# --- CONEXÃO COM O BANCO DE DADOS EM NUVEM SUPABASE ---
@st.cache_resource
def conectar_supabase() -> Client:
    """Conecta com segurança ao banco de dados usando os Secrets do Streamlit"""
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

try:
    supabase = conectar_supabase()
except Exception as e:
    st.error("Erro ao conectar ao banco de dados em nuvem. Verifique os Secrets do Streamlit.")
    st.stop()

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
        # Busca dados direto da nuvem permanente
        response = supabase.table("equipamentos").select("*").execute()
        equipamentos = response.data
        
        if equipamentos:
            for eq in equipamentos:
                st.write(f"🔹 **[{eq['id']}] {eq['nome']}** | Setor: {eq['localizacao']} | Criticidade: {eq['criticidade']}")
                if st.button("🗑️ Remover " + str(eq['id']), key="del_" + str(eq['id'])):
                    supabase.table("equipamentos").delete().eq("id", eq['id']).execute()
                    st.success("Equipamento removido do banco de dados na nuvem!")
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
                    novo_registro = {
                        "id": id_eq, "nome": nome_eq, "localizacao": local_eq, "criticidade": crit_eq,
                        "check_semanal": c_sem, "check_mensal": c_mes, "check_anual": c_ano
                    }
                    supabase.table("equipamentos").insert(novo_registro).execute()
                    st.success("Máquina registrada e salva permanentemente na nuvem!")
                    st.rerun()
                else:
                    st.error("Preencha os campos obrigatórios.")

    with aba_editar:
        st.subheader("Editar Máquina Existente")
        response = supabase.table("equipamentos").select("*").execute()
        equipamentos_lista = response.data
        opcoes_edicao = {e['id'] + " - " + e['nome']: e for e in equipamentos_lista}
        
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
                    alteracoes = {
                        "nome": novo_nome, "localizacao": novo_local, "criticidade": novo_crit,
                        "check_semanal": n_sem, "check_mensal": n_mes, "check_anual": n_ano
                    }
                    supabase.table("equipamentos").update(alteracoes).eq("id", eq_para_editar['id']).execute()
                    st.success("Alterações salvas com sucesso na nuvem!")
                    st.rerun()
# ==========================================
# 2. PÁGINA: PLANEJAMENTO TEMPORAL
# ==========================================
elif menu == "📅 Planejamento & Checklists":
    st.header("📅 Planejamento de Manutenções Preventivas")
    aba_sem, aba_mes, aba_ano, aba_novo = st.tabs(["🗓️ Semanal", "📅 Mensal", "⏳ Anual", "➕ Agendar Preventiva"])
    
    # Busca todos os planejamentos pendentes direto da nuvem
    response_plan = supabase.table("planejamento").select("*").eq("status", "Pendente").execute()
    todos_agendamentos = response_plan.data

    def renderizar_lista_preventivas(dados_filtrados):
        if dados_filtrados:
            for p in dados_filtrados:
                col_dados, col_acao = st.columns([4, 1])
                with col_dados:
                    st.write("⚙️ **" + str(p['equipamento']) + "** | 📅 **Data Prevista:** " + str(p.get('data_prevista')) + " | **Status:** " + str(p['status']))
                    st.write("🔧 Peças Programadas: " + str(p['pecas']))
                with col_acao:
                    if st.button("✔️ Concluir", key="comp_" + str(p['id'])):
                        # Salva o registro finalizado na tabela de histórico da nuvem
                        registro_historico = {
                            "equipamento": p['equipamento'],
                            "periodo": p['periodo'],
                            "data_prevista": p['data_prevista'],
                            "data_conclusao": datetime.now().strftime("%d/%m/%Y %H:%M"),
                            "pecas": p['pecas'],
                            "status": "Concluído"
                        }
                        supabase.table("historico").insert(registro_historico).execute()
                        
                        # Remove a ordem antiga da tabela de planejamento ativo na nuvem
                        supabase.table("planejamento").delete().eq("id", p['id']).execute()
                        
                        st.success("Ordem de serviço finalizada e salva permanentemente no histórico!")
                        st.rerun()
                st.write("---")
        else:
            st.info("Nenhuma manutenção preventiva pendente para este período.")

    with aba_sem:
        renderizar_lista_preventivas([a for a in todos_agendamentos if a['periodo'] == "Semanal"])

    with aba_mes:
        renderizar_lista_preventivas([a for a in todos_agendamentos if a['periodo'] == "Mensal"])

    with aba_ano:
        renderizar_lista_preventivas([a for a in todos_agendamentos if a['periodo'] == "Anual"])
    
    with aba_novo:
        st.subheader("📋 Agendar Nova Preventiva")
        # Busca os nomes das máquinas cadastradas na nuvem para preencher o seletor
        response_eq = supabase.table("equipamentos").select("nome").execute()
        lista_nomes = [row['nome'] for row in response_eq.data]
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
                    supabase.table("planejamento").insert(novo_agendamento).execute()
                    st.success("Manutenção agendada e guardada com sucesso na nuvem permanentemente!")
                    st.rerun()

# ==========================================
# 3. PÁGINA: HISTÓRICO DE TROCAS
# ==========================================
elif menu == "📜 Histórico de Trocas":
    st.header("📜 Histórico de Trocas e Manutenções Concluídas")
    # Busca os registros de manutenções finalizadas direto da tabela permanente
    response_hist = supabase.table("historico").select("*").execute()
    historico_lista = response_hist.data
    
    if historico_lista:
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

    # Busca as ordens de manutenção pendentes na nuvem
    response_pend = supabase.table("planejamento").select("*").eq("status", "Pendente").execute()
    ordens_pendentes = response_pend.data
    
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
                    id_print = "pt_print_" + str(os_dados['id'])
                    cod_pt = "PT-" + str(os_dados['id']) + datetime.now().strftime('%M%S')
                    
                    html_corpo = '<div id="' + id_print + '" style="border:3px double #FF0000; padding:20px; background-color:#FFF5F5; color:#000000; font-family:monospace; border-radius:5px; margin-bottom:20px;">'
                    html_corpo += '<h2 style="text-align:center; color:#FF0000; margin-bottom:20px;">⚠️ PERMISSÃO DE TRABALHO (PT) - REGISTRO INDUSTRIAL</h2>'
                    html_corpo += '<p><b>CÓDIGO PT:</b> ' + cod_pt + ' | <b>VINCULADO À:</b> OS #' + str(os_dados['id']) + '</p>'
                    html_corpo += '<p><b>EQUIPAMENTO:</b> ' + str(os_dados['equipamento']) + ' | <b>SERVIÇO:</b> ' + str(os_dados['pecas']) + '</p>'
                    html_corpo += "<hr style='border-top:1px dashed #FF0000;'>"
