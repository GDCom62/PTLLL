import streamlit as st
from datetime import datetime
import os
import json
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Controle de Manutenção & PT", layout="wide", page_icon="⚙️")

# --- BANCO DE DADOS PERSISTENTE EM ARQUIVO LOCAL (JSON) ---
ARQUIVO_BANCO = "banco_manutencao.json"

def carregar_dados():
    if os.path.exists(ARQUIVO_BANCO):
        try:
            with open(ARQUIVO_BANCO, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
            
    dados_padrao = {
        "maquinas": [
            {
                "id": "EQ-001", 
                "nome": "Torno Mecânico Nardini", 
                "localizacao": "Oficina Central", 
                "criticidade": "Alta", 
                "check_semanal": "1. Verificar nivel de oleo lubrificante; 2. Limpar os barramentos; 3. Lubrificar as guias lineares; 4. Remover cavacos acumulados.", 
                "check_mensal": "1. Trocar filtros de fluido refrigerante; 2. Conferir tensao das correias do motor; 3. Verificar folgas nos eixos X e Z; 4. Testar botoes de emergencia.", 
                "check_anual": "1. Revisao geral do motor eletrico; 2. Alinhamento geometrico completo; 3. Troca total do oleo da caixa de engrenagens; 4. Megagem de isolamento eletrico."
            },
            {
                "id": "EQ-002", 
                "nome": "Compressor de Ar Schulz", 
                "localizacao": "Sala de Compressores", 
                "criticidade": "Média", 
                "check_semanal": "1. Drenar condensado do reservatorio; 2. Verificar nivel de oleo do carter; 3. Checar ruidos ou vibracoes estranhas; 4. Verificar pressao de operacao.", 
                "check_mensal": "1. Limpar e inspecionar o filtro de ar; 2. Verificar vazamentos em conexoes e tubulacoes; 3. Conferir alinhamento das polias e correias; 4. Testar pressostato.", 
                "check_anual": "1. Troca completa do oleo lubrificante; 2. Substituicao do elemento do filtro de ar; 3. Teste hidrostatico e calibracao da valvula de seguranca; 4. Limpeza interna das serpentinas."
            }
        ],
        "planejamento": [
            {"id": 1, "equipamento": "Torno Mecânico Nardini", "periodo": "semanal", "data_prevista": datetime.now().strftime("%d/%m/%Y"), "pecas": "Troca de oleo das guias e limpeza dos barramentos", "status": "Pendente"}
        ],
        "historico": [
            {"id": 99, "equipamento": "Compressor de Ar Schulz", "periodo": "mensal", "data_prevista": "15/05/2026", "data_conclusao": "15/05/2026 10:00", "pecas": "Troca de filtro de ar", "status": "Concluido"}
        ]
    }
    salvar_dados(dados_padrao)
    return dados_padrao

def salvar_dados(dados):
    with open(ARQUIVO_BANCO, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

if "db" not in st.session_state:
    st.session_state.db = carregar_dados()

# --- MENU LATERAL ---
st.sidebar.markdown("**Desenvolvido por GDCOM**")
st.sidebar.title("⚙️ Gestão de Manutenção")
menu = st.sidebar.radio("Navegar para:", [
    "🔍 Lista de Máquinas",
    "➕ Cadastrar Nova Máquina",
    "📅 Planejamento & Checklists",
    "📜 Histórico de Trocas",
    "⚠️ Emissão de PT"
])

equipamentos = st.session_state.db["maquinas"]
todos_agendamentos = st.session_state.db["planejamento"]
historico_lista = st.session_state.db["historico"]

# ==========================================
# ABAS DO SISTEMA
# ==========================================
if menu == "🔍 Lista de Máquinas":
    st.header("🔍 Equipamentos Registrados")
    for idx, eq in enumerate(equipamentos):
        st.write(f"🔹 **[{eq.get('id', idx)}] {eq.get('nome')}** | Setor: {eq.get('localizacao')} | Criticidade: {eq.get('criticidade')}")
        st.write("---")

elif menu == "➕ Cadastrar Nova Máquina":
    st.header("➕ Cadastrar Nova Máquina")
    with st.form("form_cadastro_direto"):
        id_eq = st.text_input("Código/Tag do Equipamento (Ex: EQ-003):")
        nome_eq = st.text_input("Nome do Equipamento:")
        local_eq = st.text_input("Localização / Setor:")
        crit_eq = st.selectbox("Criticidade:", ["Baixa", "Média", "Alta"])
        st.markdown("##### 📜 Ações Preventivas Recomendadas")
        c_sem = st.text_area("Checklist Semanal:", "1. Verificar nivel de oleo; 2. Limpeza geral")
        c_mes = st.text_area("Checklist Mensal:", "1. Trocar filtros; 2. Conferir correias")
        c_ano = st.text_area("Checklist Anual:", "1. Revisao geral do motor")
        botao_salvar = st.form_submit_button("Salvar Equipamento")
        
    if botao_salvar and id_eq and nome_eq:
        payload = {"id": id_eq, "nome": nome_eq, "localizacao": local_eq, "criticidade": crit_eq, "check_semanal": c_sem, "check_mes": c_mes, "check_anual": c_ano}
        st.session_state.db["maquinas"].append(payload)
        salvar_dados(st.session_state.db)
        st.success("🎉 Equipamento gravado permanentemente!")
        st.rerun()

elif menu == "📅 Planejamento & Checklists":
    st.header("📅 Planejamento de Manutenções Preventivas")
    st.subheader("📋 Consulta Rápida de Ações Preventivas")
    opcoes_lista = {eq.get('nome', 'Máquina'): eq for eq in equipamentos}
    maquina_selecionada = st.selectbox("Selecione uma máquina:", list(opcoes_lista.keys()))
    
    if maquina_selecionada:
        dados_mq = opcoes_lista[maquina_selecionada]
        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1: st.info(f"**Semanal:**\n{dados_mq.get('check_semanal', 'Nao configurado.')}")
        with col_c2: st.warning(f"**Mensal:**\n{dados_mq.get('check_mes', 'Nao configurado.')}")
        with col_c3: st.error(f"**Anual:**\n{dados_mq.get('check_anual', 'Nao configurado.')}")
            
    st.markdown("---")
    st.subheader("📅 Agendar Nova Intervenção")
    with st.form("form_agenda_direto"):
        lista_nomes = list(opcoes_lista.keys())
        eq_escolhido = st.selectbox("Selecione a Máquina Alvo:", lista_nomes if lista_nomes else ["Nenhum cadastrado"])
        periodo_escolhido = st.selectbox("Escolha o Período:", ["Semanal", "Mensal", "Anual"])
        data_planejada = st.date_input("Selecione a Data:", datetime.now())
        pecas_necessarias = st.text_area("Descrição das Peças / Ferramentas / Escopo:", value="Realizar rotina padrao de preventiva.")
        botao_agenda = st.form_submit_button("💾 Gravar e Agendar Manutenção")
        
    if botao_agenda and eq_escolhido != "Nenhum cadastrado":
        novo_agendamento = {"id": len(todos_agendamentos) + 1, "equipamento": eq_escolhido, "periodo": periodo_escolhido, "data_prevista": data_planejada.strftime("%d/%m/%Y"), "pecas": pecas_necessarias, "status": "Pendente"}
        st.session_state.db["planejamento"].append(novo_agendamento)
        salvar_dados(st.session_state.db)
        st.success("🎉 Agendamento registrado!")
        st.rerun()

    st.markdown("---")
    st.subheader("🔍 Ordens de Serviço Abertas")
    ordens_pendentes = [os for os in todos_agendamentos if os.get("status") == "Pendente"]
    
    for idx, p in enumerate(ordens_pendentes):
        st.write(f"⚙️ **{p.get('equipamento')}** | Período: **{p.get('periodo')}** | 📅 **Prevista:** {p.get('data_prevista')}")
        st.write(f"🔧 Peças/Ferramentas: {p.get('pecas')}")
        if st.button("✔️ Concluir OS e Enviar para Histórico", key=f"comp_{idx}"):
            registro_h = {"id": p.get('id'), "equipamento": p.get('equipamento'), "periodo": p.get('periodo'), "data_prevista": p.get('data_prevista'), "data_conclusao": datetime.now().strftime("%d/%m/%Y %H:%M"), "pecas": p.get('pecas'), "status": "Concluido"}
            st.session_state.db["historico"].append(registro_h)
            for item in st.session_state.db["planejamento"]:
                if item.get("id") == p.get("id"):
                    item["status"] = "Concluido"
            salvar_dados(st.session_state.db)
            st.success("Ordem finalizada e salva permanentemente!")
            st.rerun()
        st.write("---")

elif menu == "📜 Histórico de Trocas":
    st.header("📜 Histórico de Serviços Concluídos")
    st.subheader("📊 Gráfico de Evolução dos Serviços por Período")
    
    ordens_abertas = [os for os in todos_agendamentos if os.get("status") == "Pendente"]
    p_semanal = sum(1 for x in ordens_abertas if str(x.get('periodo')).lower() == 'semanal')
    p_mensal = sum(1 for x in ordens_abertas if str(x.get('periodo')).lower() == 'mensal')
    p_anual = sum(1 for x in ordens_abertas if str(x.get('periodo')).lower() == 'anual')
    
    c_semanal = sum(1 for x in historico_lista if str(x.get('periodo')).lower() == 'semanal')
    c_mensal = sum(1 for x in historico_lista if str(x.get('periodo')).lower() == 'mensal')
    c_anual = sum(1 for x in historico_lista if str(x.get('periodo')).lower() == 'anual')
    
    dados_grafico = {
        "Período": ["Semanal", "Mensal", "Anual"],
        "Pendentes (Abertas)": [p_semanal, p_mensal, p_anual],
        "Concluídos (Histórico)": [c_semanal, c_mensal, c_anual]
    }
    df = pd.DataFrame(dados_grafico).set_index("Período")
    st.bar_chart(df)
    
    st.markdown("---")
    st.subheader("📋 Listagem Completa de Ordens Fechadas")
    for h in historico_lista:
        st.write(f"✅ **{h.get('equipamento')}** | Período: **{h.get('periodo')}**")
        st.write(f"⏱️ **Concluído em:** {h.get('data_conclusao', 'N/A')} | Intervenção realizada: {h.get('pecas')}")
        st.write("---")

elif menu == "⚠️ Emissão de PT":
    st.header("⚠️ Permissão de Trabalho (PT) & Segurança Industrial")
    
    ordens_ativas = [os for os in todos_agendamentos if os.get("status") == "Pendente"]
    if not ordens_ativas or len(ordens_ativas) == 0:
        st.warning("Não existem manutenções preventivas pendentes abertas para gerar PT.")
    else:
        opcoes_os = {f"OS #{p.get('id', idx)} - {p.get('equipamento')} ({p.get('periodo')})": p for idx, p in enumerate(ordens_ativas)}

# ==========================================
# 4. PÁGINA: EMISSÃO DE PT (TOTALMENTE DESACOPLADA)
# ==========================================
elif menu == "⚠️ Emissão de PT":
    st.header("⚠️ Emissão e Impressão de Permissão de Trabalho (PT)")
    
    # 1. Filtra as manutenções pendentes registradas no sistema
    ordens_pendentes = [p for p in st.session_state.planejamento if p['status'] == "Pendente"]
    
    if not ordens_pendentes:
        st.warning("Não existem manutenções pendentes no momento para emitir uma PT. Agende uma preventiva primeiro!")
    else:
        # Monta a lista de opções para o seletor
        opcoes_os = {f"OS #{p['id']} - {p['equipamento']} ({p['periodo']})": p for p in ordens_pendentes}
        os_selecionada_str = str(st.selectbox("Selecione a Ordem de Serviço para vincular à PT:", list(opcoes_os.keys())))
        os_dados = opcoes_os[os_selecionada_str]
        
        st.markdown("---")
        st.subheader("📋 Formulário de Liberação de Segurança")
        
        # Formulário isolado para preenchimento dos dados da PT
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
            
        # 2. Processamento do documento após o clique (Simulação de Impressão Industrial)
        if bt_gerar:
            if not executante:
                st.error("Por favor, preencha o nome do técnico executante para assinar a ordem.")
            else:
                st.success("✅ Permissão de Trabalho gerada com sucesso na memória do sistema!")
                
                # Layout pronto para impressão (Preview do Documento Industrial)
                st.markdown("""
                <style>
                    .pt-box {
                        border: 3px double #FF0000;
                        padding: 20px;
                        background-color: #FFF5F5;
                        color: #000000;
                        font-family: monospace;
                        border-radius: 5px;
                    }
                    .pt-title { text-align: center; color: #FF0000; margin-bottom: 20px; }
                </style>
                """, unsafe_html=True)
                
                # Monta a string visual do documento para o usuário
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
                
                # Botão nativo para baixar como arquivo de texto (ou você pode usar Ctrl+P para imprimir a tela)
                st.download_button(
                    label="🖨️ Baixar Cópia do Texto para Impressão",
                    data=conteudo_pt.replace("<br>", "\n").replace("<p>", "").replace("</p>", "\n").replace("<div>", "").replace("</div>", ""),
                    file_name=f"PT_OS_{os_dados['id']}.txt",
                    mime="text/plain"
                )
