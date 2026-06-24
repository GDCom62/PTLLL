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
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT equipamento, data_prevista, pecas, periodo FROM planejamento WHERE status='Pendente'")
    todos_agendamentos = cursor.fetchall()
    conn.close()
    
    with aba_sem:
        dados_sem = [a for a in todos_agendamentos if a[3] == "Semanal"]
        if dados_sem:
            for p in dados_sem:
                st.write(f"⚙️ **{p[0]}** | 📅 **Data:** {p[1]} | **Status:** Pendente")
                st.write(f"🔧 Peças Programadas: {p[2]}")
                st.write("---")
        else:
            st.info("Nenhuma preventiva semanal pendente.")

    with aba_mes:
        dados_mes = [a for a in todos_agendamentos if a[3] == "Mensal"]
        if dados_mes:
            for p in dados_mes:
