# ==========================================
# 4. PÁGINA: EMISSÃO DE PT (TOTALMENTE DESACOPLADA)
# ==========================================
elif menu == "⚠️ Emissão de PT":
    st.header("⚠️ Emissão e Impressão de Permissão de Trabalho (PT)")
    
    # Inicializa o estado para guardar a PT gerada e não deixá-la sumir
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
                
                # Injeta os estilos CSS necessários para renderização e impressão limpa
                st.markdown(f"""
                <style>
                    #{id_impressao} {{
                        border: 3px double #FF0000;
                        padding: 20px;
                        background-color: #FFF5F5;
                        color: #000000;
                        font-family: monospace;
                        border-radius: 5px;
                        margin-bottom: 20px;
                    }}
                    .pt-title {{ text-align: center; color: #FF0000; margin-bottom: 20px; }}
                    
                    @media print {{
                        body * {{ visibility: hidden; }}
                        #{id_impressao}, #{id_impressao} * {{ visibility: visible; }}
                        #{id_impressao} {{
                            position: absolute;
                            left: 0;
                            top: 0;
                            width: 100%;
                            border: 2px solid #000000 !important;
                            background-color: #FFFFFF !important;
                        }}
                    }}
                </style>
                """, unsafe_html=True)
                
                conteudo_pt = f"""
                <div id="{id_impressao}">
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
                    {"[X] AREA ISOLADA<br>" if c_delim else ""}
                    {"[X] EPIs VERIFICADOS<br>" if c_epi else ""}
                    {"[X] PROTECAO INCENDIO PRONTA<br>" if c_extintor else ""}
                    </p>
                    <p><b>OBSERVAÇÕES:</b> {observacoes_seg}</p>
                    <br><br><br>
                    <p style='text-align: center;'>________________________________________<br>Assinatura Digital do Supervisor (Liberado)</p>
                </div>
                """
                
                # Salva no estado para congelar na tela sem sumir
                st.session_state.pt_gerada_html = conteudo_pt
                st.session_state.pt_gerada_txt = conteudo_pt.replace("<br>", "\n").replace("<p>", "").replace("</p>", "\n").replace("<div>", "").replace("</div>", "")
                st.session_state.pt_id_atual = os_dados['id']
                st.success("✅ Permissão de Trabalho gerada com sucesso!")
                st.rerun()

        # Exibe a PT de forma fixa se ela já tiver sido criada na sessão
        if st.session_state.pt_gerada_html:
            st.markdown("---")
            st.subheader("📄 Documento de PT Ativo")
            st.markdown(st.session_state.pt_gerada_html, unsafe_html=True)
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                st.markdown("""
                    <button onclick="window.print()" style="
                        background-color: #FF4B4B; 
                        color: white; 
                        border: none; 
                        padding: 0.5rem 1rem; 
                        border-radius: 0.25rem; 
                        cursor: pointer;
                        font-weight: bold;
                        width: 100%;
                        height: 45px;
                    ">🖨️ Mandar para Impressora / Salvar PDF</button>
                """, unsafe_html=True)
            
            with col_btn2:
                st.download_button(
                    label="📄 Baixar Cópia do Texto (.txt)",
                    data=st.session_state.pt_gerada_txt,
                    file_name=f"PT_OS_{st.session_state.pt_id_atual}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
