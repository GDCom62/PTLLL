import streamlit as st
from datetime import datetime
import os
import requests

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Controle de Manutenção & PT", layout="wide", page_icon="⚙️")

# --- CONEXÃO AVANÇADA COM DIAGNÓSTICO SUPABASE ---
SUB_URL = ""
SUB_HEADERS = {}
MODO_DEMO = False
STATUS_CONEXAO = "Não configurado"

try:
    if "SUPABASE_URL" in st.secrets and "SUPABASE_KEY" in st.secrets:
        SUB_URL = str(st.secrets["SUPABASE_URL"]).strip().rstrip("/")
        key_limpa = str(st.secrets["SUPABASE_KEY"]).strip()
        
        SUB_HEADERS = {
            "apikey": key_limpa,
            "Authorization": f"Bearer {key_limpa}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
        STATUS_CONEXAO = "Chaves carregadas. Prontos para testar rotas."
    else:
        MODO_DEMO = True
        STATUS_CONEXAO = "Secrets 'SUPABASE_URL' ou 'SUPABASE_KEY' ausentes no Streamlit Cloud."
except Exception as e:
    MODO_DEMO = True
    STATUS_CONEXAO = f"Erro crítico ao ler Secrets: {e}"

# --- INICIALIZAÇÃO DA MEMÓRIA DE SEGURANÇA LOCAL ---
if "maquinas_locais" not in st.session_state:
    st.session_state.maquinas_locais = [
        {"id": "EQ-001", "nome": "Torno Mecânico Nardini", "localizacao": "Oficina Central", "criticidade": "Alta", "check_semanal": "Óleo e limpeza", "check_mensal": "Filtros", "check_anual": "Motor"},
        {"id": "EQ-002", "nome": "Compressor de Ar Schulz", "localizacao": "Sala de Compressores", "criticidade": "Média", "check_semanal": "Drenar", "check_mensal": "Filtro", "check_anual": "Válvulas"}
    ]
if "planejamento_local" not in st.session_state:
    st.session_state.planejamento_local = []
if "historico_local" not in st.session_state:
    st.session_state.historico_local = []

# --- MARCA DA EMPRESA EM NUVEM NO MENU LATERAL ---
st.sidebar.markdown("**Desenvolvido por GDCOM**")
st.sidebar.title("⚙️ Gestão de Manutenção")

# Painel visual de diagnóstico de rede
st.sidebar.subheader("📡 Status da Nuvem")
if MODO_DEMO:
    st.sidebar.error("🔴 Rodando em MODO LOCAL (Sem nuvem)")
else:
    st.sidebar.success("🟢 Configurações de Nuvem Ativas")

menu = st.sidebar.radio("Navegar para:", [
    "🔍 Lista de Máquinas",
    "➕ Cadastrar Nova Máquina",
    "✏️ Editar Máquina",
    "📅 Planejamento & Checklists",
    "📜 Histórico de Trocas",
    "⚠️ Emissão de PT",
    "🛠️ Diagnóstico de Conexão"
])

# --- CARREGAMENTO GLOBAL DE DADOS ---
equipamentos = []
if not MODO_DEMO:
    try:
        req = requests.get(f"{SUB_URL}/rest/v1/equipamentos?select=*&order=id.asc", headers=SUB_HEADERS, timeout=5)
        if req.status_code == 200:
            equipamentos = req.json()
            STATUS_CONEXAO = "Conectado e sincronizado com a tabela 'equipamentos'!"
        else:
            STATUS_CONEXAO = f"Erro HTTP {req.status_code} ao ler equipamentos. Tabela existe?"
    except Exception as e:
        STATUS_CONEXAO = f"Falha de conexão com a URL do Supabase: {e}"

if not equipamentos:
    equipamentos = st.session_state.maquinas_locais

# ==========================================
# PAGE: DIAGNÓSTICO DE CONEXÃO
# ==========================================
if menu == "🛠️ Diagnóstico de Conexão":
    st.header("🛠️ Painel Analítico de Conexão com o Supabase")
    st.write("Use esta tela para entender exatamente por que o banco de dados está recusando as gravações.")
    
    st.markdown("### 📊 Relatório Técnico Atual")
    st.code(f"URL Alvo: {SUB_URL}\nHeaders Carregados: {len(SUB_HEADERS) > 0}\nModo Local Ativo: {MODO_DEMO}\nDiagnóstico: {STATUS_CONEXAO}")
    
    if st.button("⚡ Executar Teste de Gravação Forçado"):
        st.write("Enviando registro de teste para a tabela `equipamentos`...")
        teste_payload = {"id": "TESTE-999", "nome": "Equipamento Teste Conexão", "localizacao": "Laboratório", "criticidade": "Baixa"}
        
        try:
            res = requests.post(f"{SUB_URL}/rest/v1/equipamentos", json=teste_payload, headers=SUB_HEADERS, timeout=5)
            if res.status_code == 201 or res.status_code == 200:
                st.success("🎉 SUCESSO! O Supabase aceitou a gravação direta. A conexão está perfeita.")
                requests.delete(f"{SUB_URL}/rest/v1/equipamentos?id=eq.TESTE-999", headers=SUB_HEADERS, timeout=5)
            else:
                st.error("❌ O Supabase RECUSOU a gravação externa.")
                st.error(f"Código do Erro HTTP: {res.status_code}")
                st.markdown("**Possíveis causas para este código:**")
                st.write("- **401/403**: Suas chaves de Secrets do Streamlit estão erradas ou expiraram.")
                st.write("- **404**: A tabela com o nome exato `equipamentos` não existe no seu painel do Supabase.")
                st.write("- **400**: Os nomes de colunas no seu banco (ex: id, nome, localizacao) estão diferentes do código Python.")
                st.code(res.text)
        except Exception as e:
            st.error(f"❌ Erro de rede intransponível: {e}. Verifique se a URL do Supabase não possui espaços ou erros de digitação.")

# ==========================================
# PAGE 1: LISTA DE MÁQUINAS
# ==========================================
elif menu == "🔍 Lista de Máquinas":
    st.header("🔍 Equipamentos Registrados no Sistema")
    if equipamentos:
        for idx, eq in enumerate(equipamentos):
            st.write(f"🔹 **[{eq['id']}] {eq['nome']}** | Setor: {eq['localizacao']} | Criticidade: {eq['criticidade']}")
            if st.button("🗑️ Remover " + str(eq['id']), key="del_" + str(eq['id']) + "_" + str(idx)):
                if not MODO_DEMO:
                    try:
                        res = requests.delete(f"{SUB_URL}/rest/v1/equipamentos?id=eq.{eq['id']}", headers=SUB_HEADERS, timeout=5)
                        if res.status_code != 200 and res.status_code != 204:
                            st.error(f"Erro Supabase: {res.status_code} - {res.text}")
                    except Exception as e:
                        st.error(f"Falha de rede: {e}")
                st.session_state.maquinas_locais = [m for m in st.session_state.maquinas_locais if m['id'] != eq['id']]
                st.success("Equipamento removido!")
                st.rerun()
            st.write("---")

# ==========================================
# PAGE 2: CADASTRAR MÁQUINA
# ==========================================
elif menu == "➕ Cadastrar Nova Máquina":
    st.header("➕ Cadastrar Nova Máquina")
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
                novo_registro = {"id": id_eq, "nome": nome_eq, "localizacao": local_eq, "criticidade": crit_eq, "check_semanal": c_sem, "check_mes": c_mes, "check_anual": c_ano}
                st.session_state.maquinas_locais.append(novo_registro)
                if not MODO_DEMO:
                    try:
                        res = requests.post(f"{SUB_URL}/rest/v1/equipamentos", json=novo_registro, headers=SUB_HEADERS, timeout=5)
                        if res.status_code == 201 or res.status_code == 200:
                            st.success("Gravado com sucesso no Supabase!")
                        else:
                            st.error(f"Supabase recusou: {res.status_code} - {res.text}")
                    except Exception as e:
                        st.error(f"Falha de rede: {e}")
                st.rerun()
            else:
                st.error("Preencha os campos obrigatórios.")

# ==========================================
# PAGE 3: EDITAR MÁQUINA
# ==========================================
elif menu == "✏️ Editar Máquina":
    st.header("✏️ Editar Máquina Existente")
    opcoes_edicao = {str(e['id']) + " - " + str(e['nome']): e for e in equipamentos if isinstance(e, dict) and 'id' in e}
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
                alteracoes = {"nome": novo_nome, "localizacao": novo_local, "criticidade": novo_crit, "check_semanal": n_sem, "check_mensal": n_mes, "check_anual": n_ano}
                if not MODO_DEMO:
                    try:
                        res = requests.patch(f"{SUB_URL}/rest/v1/equipamentos?id=eq.{eq_para_editar['id']}", json=alteracoes, headers=SUB_HEADERS, timeout=5)
                        if res.status_code != 200 and res.status_code != 204:
                            st.error(f"Erro Supabase: {res.status_code} - {res.text}")
                    except Exception as e:
