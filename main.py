import streamlit as st
import requests

st.set_page_config(page_title="Teste de Conexão", layout="wide")
st.title("⚡ Teste de Gravação Direta no Supabase")

# Recupera credenciais dos Secrets
try:
    url_banco = st.secrets["supabase"]["url"].strip().rstrip("/")
    chave_banco = st.secrets["supabase"]["key"].strip()
except Exception as e:
    st.error(f"Erro nos Secrets: {e}")
    url_banco, chave_banco = None, None

if url_banco and chave_banco:
    st.success("✅ Secrets carregados com sucesso no Streamlit!")
    
    st.subheader("➕ Cadastrar Nova Máquina de Teste")
    with st.form("form_teste"):
        id_teste = st.text_input("Tag Única (Ex: EQ-999):").strip()
        nome_teste = st.text_input("Nome da Máquina:").strip()
        botao = st.form_submit_button("Testar Gravação no Supabase")
        
    if botao:
        if not id_teste or not nome_teste:
            st.error("Preencha a Tag e o Nome.")
        else:
            payload = {
                "id": id_teste,
                "nome": nome_teste,
                "localizacao": "Teste",
                "criticidade": "Média",
                "check_semanal": "Teste",
                "check_mensal": "Teste",
                "check_anual": "Teste"
            }
            headers = {
                "apikey": chave_banco,
                "Authorization": f"Bearer {chave_banco}",
                "Content-Type": "application/json"
            }
            url_api = f"{url_banco}/rest/v1/maquinas"
            
            try:
                response = requests.post(url_api, headers=headers, json=payload)
                st.info(f"Código de resposta do banco: {response.status_code}")
                # LINHA 47 CORRIGIDA DEFINITIVAMENTE:
                if 200 <= response.status_code <= 299:
                    st.success("🎉 GRAVAÇÃO INDUSTRIAL CONFIRMADA NO SUPABASE!")
                else:
                    st.error(f"O banco recusou os dados. Detalhe técnico: {response.text}")
            except Exception as e:
                st.error(f"Erro na requisição: {e}")
