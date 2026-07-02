import streamlit as st
from datetime import datetime
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Controle de Manutenção & PT", layout="wide", page_icon="⚙️")

# --- INICIALIZAÇÃO DA MEMÓRIA DE SEGURANÇA LOCAL ---
if "maquinas" not in st.session_state:
    st.session_state.maquinas = [
        {"id": "EQ-001", "nome": "Torno Mecânico Nardini", "localizacao": "Oficina Central", "criticidade": "Alta", "check_semanal": "1. Verificar nível de óleo; 2. Limpar barramento.", "check_mensal": "1. Trocar filtros; 2. Conferir correias.", "check_anual": "1. Revisão do motor."},
        {"id": "EQ-002", "nome": "Compressor de Ar Schulz", "localizacao": "Sala de Compressores", "criticidade": "Média", "check_semanal": "1. Drenar reservatório; 2. Checar ruídos.", "check_mensal": "1. Limpar filtro; 2. Verificar conexões.", "check_anual": "1. Teste de válvula."}
    ]

if "planejamento" not in st.session_state:
    st.session_state.planejamento = [
        {"id": 1, "equipamento": "Torno Mecânico Nardini", "periodo": "Semanal", "data_prevista": datetime.now().strftime("%d/%m/%Y"), "pecas": "Troca de óleo das guias e limpeza", "status": "Pendente", "seguranca": "Cuidado com partes giratórias."}
    ]

if "historico" not in st.session_state:
    st.session_state.historico = [
        {"id": 99, "equipamento": "Compressor de Ar Schulz", "periodo": "Mensal", "data_prevista": "15/05/2026", "data_conclusao": "15/05/2026 10:00", "pecas": "Troca de filtro de ar", "status": "Concluido"}
    ]

# Estados de controle para edição
if "editando_maquina_id" not in st.session_state:
    st.session_state.editando_maquina_id = None
if "editando_os_id" not in st.session_state:
    st.session_state.editando_os_id = None

# --- MENU LATERAL ---
st.sidebar.markdown("**Desenvolvido por GDCOM**")
st.sidebar.title("⚙️ Gestão de Manutenção")
menu = st.sidebar.radio("Navegar para:", [
    "🔍 Abas 1 & 2: Gerenciar Máquinas",
    "📅 Aba 3: Ordens de Serviço (OS)",
    "📜 Aba 4: Histórico de Trocas",
    "⚠️ Aba 5: Emissão de PT"
])

# ==========================================
# ABAS 1 & 2: LISTA E CADASTRO DE MÁQUINAS (COM EDIÇÃO E EXCLUSÃO)
# ==========================================
if menu == "🔍 Abas 1 & 2: Gerenciar Máquinas":
    st.header("🔍 Gerenciamento de Equipamentos")
    
    # Formulário de Cadastro ou Edição de Máquina
    if st.session_state.editando_maquina_id is not None:
        st.subheader("✏️ Editar Equipamento Registrado")
        mq_editar = next((m for m in st.session_state.maquinas if m["id"] == st.session_state.editando_maquina_id), None)
        
        if mq_editar:
            with st.form("form_editar_maquina"):
                edit_nome = st.text_input("Nome do Equipamento:", value=mq_editar["nome"])
                edit_local = st.text_input("Localização / Setor:", value=mq_editar["localizacao"])
                edit_crit = st.selectbox("Criticidade:", ["Baixa", "Média", "Alta"], index=["Baixa", "Média", "Alta"].index(mq_editar["criticidade"]))
                edit_sem = st.text_area("Checklist Semanal:", value=mq_editar["check_semanal"])
                edit_mes = st.text_area("Checklist Mensal:", value=mq_editar["check_mensal"])
                edit_ano = st.text_area("Checklist Anual:", value=mq_editar["check_anual"])
                
                c1, col2 = st.columns(2)
                with c1: btn_salvar_mq = st.form_submit_button("💾 Salvar Alterações")
                with col2: btn_canc_mq = st.form_submit_button("❌ Cancelar")
                
            if btn_salvar_mq:
                mq_editar["nome"] = edit_nome
                mq_editar["localizacao"] = edit_local
                mq_editar["criticidade"] = edit_crit
                mq_editar["check_semanal"] = edit_sem
                mq_editar["check_mensal"] = edit_mes
                mq_editar["check_anual"] = edit_ano
                st.session_state.editando_maquina_id = None
                st.success("Equipamento atualizado!")
                st.rerun()
            if btn_canc_mq:
                st.session_state.editando_maquina_id = None
                st.rerun()
    else:
        st.subheader("➕ Cadastrar Nova Máquina")
        with st.form("form_cadastro_direto"):
            id_eq = st.text_input("Tag do Equipamento (Ex: EQ-003):")
            nome_eq = st.text_input("Nome do Equipamento:")
            local_eq = st.text_input("Localização / Setor:")
            crit_eq = st.selectbox("Criticidade:", ["Baixa", "Média", "Alta"])
            st.markdown("##### 📜 Ações Preventivas")
            c_sem = st.text_area("Checklist Semanal:", "1. Verificar nível de óleo; 2. Limpeza.")
            c_mes = st.text_area("Checklist Mensal:", "1. Troca de filtros.")
            c_ano = st.text_area("Checklist Anual:", "1. Revisão preventiva.")
            botao_salvar = st.form_submit_button("Salvar Novo Equipamento")
            
        if botao_salvar and id_eq and nome_eq:
            st.session_state.maquinas.append({"id": id_eq, "nome": nome_eq, "localizacao": local_eq, "criticidade": crit_eq, "check_semanal": c_sem, "check_mensal": c_mes, "check_anual": c_ano})
            st.success("Equipamento cadastrado!")
            st.rerun()

    st.markdown("---")
    st.subheader("📋 Lista de Equipamentos Registrados")
    if not st.session_state.maquinas:
        st.info("Nenhuma máquina cadastrada.")
    else:
        for mq in st.session_state.maquinas:
            st.write(f"🔹 **[{mq['id']}] {mq['nome']}** | Setor: {mq['localizacao']} | Criticidade: {mq['criticidade']}")
            
            c_m1, c_m2 = st.columns(2)
            with c_m1:
                if st.button(f"✏️ Editar {mq['id']}", key=f"ed_mq_{mq['id']}"):
                    st.session_state.editando_maquina_id = mq['id']
                    st.rerun()
            with c_m2:
                if st.button(f"🗑️ Excluir {mq['id']}", key=f"ex_mq_{mq['id']}"):
                    st.session_state.maquinas = [m for m in st.session_state.maquinas if m["id"] != mq["id"]]
                    st.warning("Equipamento excluído!")
                    st.rerun()
            st.write("---")

# ==========================================
# ABA 3: PLANEJAMENTO E ORDENS DE SERVIÇO (COM EDIÇÃO E EXCLUSÃO)
# ==========================================
elif menu == "📅 Aba 3: Ordens de Serviço (OS)":
    st.header("📅 Planejamento & Ordens de Serviço (OS)")
    
    if st.session_state.editando_os_id is not None:
        st.subheader("📝 Editar Ordem de Serviço Ativa")
        os_editar = next((item for item in st.session_state.planejamento if item["id"] == st.session_state.editando_os_id), None)
        
        if os_editar:
            with st.form("form_editar_os"):
                edit_equip = st.selectbox("Máquina Alvo:", [m["nome"] for m in st.session_state.maquinas], index=[m["nome"] for m in st.session_state.maquinas].index(os_editar["equipamento"]) if os_editar["equipamento"] in [m["nome"] for m in st.session_state.maquinas] else 0)
                edit_periodo = st.selectbox("Escolha o Período:", ["Semanal", "Mensal", "Anual"], index=["semanal", "mensal", "anual"].index(os_editar["periodo"].lower()))
                edit_data = st.date_input("Data Prevista:", datetime.strptime(os_editar["data_prevista"], "%d/%m/%Y"))
                edit_pecas = st.text_area("Escopo do Serviço:", value=os_editar["pecas"])
                edit_seg = st.text_area("Observações de Segurança:", value=os_editar.get("seguranca", ""))
                
                col_b1, col_b2 = st.columns(2)
                with col_b1: btn_salvar_os = st.form_submit_button("💾 Salvar OS")
                with col_b2: btn_canc_os = st.form_submit_button("❌ Cancelar")
                
            if btn_salvar_os:
                os_editar["equipamento"] = edit_equip
                os_editar["periodo"] = edit_periodo
                os_editar["data_prevista"] = edit_data.strftime("%d/%m/%Y")
                os_editar["pecas"] = edit_pecas
                os_editar["seguranca"] = edit_seg
                st.session_state.editando_os_id = None
                st.success("Ordem de Serviço atualizada!")
                st.rerun()
            if btn_canc_os:
                st.session_state.editando_os_id = None
                st.rerun()
    else:
        st.subheader("📅 Agendar Nova Manutenção / Gerar OS")
        with st.form("form_agenda_direto"):
            lista_nomes = [m["nome"] for m in st.session_state.maquinas]
            eq_escolhido = st.selectbox("Selecione a Máquina Alvo:", lista_nomes if lista_nomes else ["Nenhum cadastrado"])
            periodo_escolhido = st.selectbox("Escolha o Período:", ["Semanal", "Mensal", "Anual"])
            data_planejada = st.date_input("Selecione a Data:", datetime.now())
            pecas_necessarias = st.text_area("Descrição das Peças / Escopo:", value="Realizar rotina padrão de preventiva.")
            seg_necessaria = st.text_area("Observações Iniciais de Segurança:", value="Seguir as NRs de segurança aplicadas.")
            botao_agenda = st.form_submit_button("💾 Gerar OS Pendente")
            
        if botao_agenda and eq_escolhido != "Nenhum cadastrado":
            novo_id = max([item["id"] for item in st.session_state.planejamento], default=0) + 1
            st.session_state.planejamento.append({"id": novo_id, "equipamento": eq_escolhido, "periodo": periodo_escolhido, "data_prevista": data_planejada.strftime("%d/%m/%Y"), "pecas": pecas_necessarias, "status": "Pendente", "seguranca": seg_necessaria})
            st.success(f"🎉 OS #{novo_id} gerada!")
            st.rerun()

    st.markdown("---")
    st.subheader("🔍 Ordens de Serviço Abertas")
    ordens_ativas = [os for os in st.session_state.planejamento if os["status"] == "Pendente"]
    
    if not ordens_ativas:
        st.info("Nenhuma Ordem de Serviço aberta.")
    else:
        for p in ordens_ativas:
