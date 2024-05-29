import streamlit as st
from streamlit_option_menu import option_menu
from docxtpl import DocxTemplate
import pandas as pd
import numpy as np
import locale
import os
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')


# CONFIGURAR AS DEFINIÇÕES DA PAGINA
st.set_page_config(
    page_title="SE-CAMEX",
    # page_icon=img,
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)



# PEGAR AS CONFIGURAÇÕES DO CSS
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# horizontal menu
selected = option_menu(None, ["Sobre", "Configurações", "Gerar Nota Técnica"], 
    icons=['house', 'gear', 'cloud-upload'], 
    menu_icon="cast", default_index=0, orientation="horizontal")


if selected == "Sobre":
    st.header("Sobre", divider='red')
    with st.container():
        st.write("Este sistema foi concebido com o propósito de automatizar uma parcela do processo de preenchimento das Notas Técnicas da Secretaria Executiva da Câmara de Comércio Exterior (SE-CAMEX)")
        st.write("")
        st.write("")
        st.write("")
        st.subheader('Contato')
        st.write("Originalmente desenvolvido por Caroline Leite (caroline.leite@planejamento.gov.br) e Raphael Amaro (raphael.amaro@planejamento.gov.br).")

if selected == "Configurações":
    st.header("Configurações")
    with st.form("conf"):
        #NCM
        if 'NCM_COD' not in st.session_state:
            NCM_COD_input = st.text_input('Código NCM:', '28230010')
        else:
            NCM_COD_input = st.text_input('Código NCM:', st.session_state['NCM_COD'])

        #Ano_inicial
        if 'ano1' not in st.session_state:
            ano1_input, ano2_input = st.select_slider('Período temporal da análise:', options=['2018', '2019', '2020', '2021', '2022', '2023', '2024'], value=('2019', '2024'))
        else:
            ano1_input, ano2_input = st.select_slider('Período temporal da análise:', options=['2018', '2019', '2020', '2021', '2022', '2023', '2024'], value=(st.session_state['ano1'], st.session_state['ano2']))

        salvar_conf = st.form_submit_button('Salvar')

            
    if salvar_conf:
        st.session_state['ano1'] = ano1_input
        st.session_state['ano2'] = ano2_input
        st.session_state['NCM_COD'] = NCM_COD_input

        st.success('Salvo com sucesso!', icon="✅")




if selected == "Gerar Nota Técnica":
    st.header("Gerar Nota Técnica")
    with st.form("plan"):
        st.info('Atenção: É imprescindível que todas as informações sejam preenchidas e devidamente salvas na seção designada como "Configurações" antes da geração das informações!', icon="⚠️")

        exportar = st.form_submit_button('Gerar informações')

            
    if exportar:
        if 'ano1' not in st.session_state:
            st.error('É obrigatório que o período temporal de análise seja inserido e salvo nas Configurações!', icon="🚨")
        elif 'NCM_COD' not in st.session_state:
            st.error('É obrigatório que o código NCM de análise seja inserido e salvo nas Configurações!', icon="🚨")

        else:

            try:
                df_ncm = int(st.session_state['NCM_COD'].replace('.',''))

                df_ncm2 = str(df_ncm)
                df_ncm3 = df_ncm2[0:4]+'.'+df_ncm2[4:6]+'.'+df_ncm2[6:8]
                
                ano1_INT = int(st.session_state['ano1'])
                ano2_INT = int(st.session_state['ano2'])

                #NCM (colocar pontos na string)
                NCM_COD_C = str(st.session_state['NCM_COD']).replace('.','')
                NCM_COD_C = NCM_COD_C[0:4]+'.'+NCM_COD_C[4:6]+'.'+NCM_COD_C[6:8]

                # IMPORTAÇÕES
                st.warning(f'Gerando dados do código NCM: {df_ncm3}! Esse processo pode ser demorado, aguarde!')

                #Importando dados

                # IMPORTAÇÕES

                #Definindo a pasta
                path = 'IMP'
                #ler os arquivos da pasta Planilhas
                files = sorted(os.listdir(path))

                batch_no = 1

                print(files)
                #looping para ler os arquivos e gerar as NTs
                for i in files:
                    if i == '.DS_Store':
                        pass
                    else:
                        if batch_no == 1:
                            df_imp = pd.read_csv(path+'/'+i, sep=',')
                            batch_no += 1
                        else:
                            df_imp2 = pd.read_csv(path+'/'+i, sep=',')
                            df_imp = pd.concat([df_imp, df_imp2])
                
            
                # EXPORTAÇÕES
                
                #Definindo a pasta
                path = 'EXP'
                #ler os arquivos da pasta Planilhas
                files = os.listdir(path)

                batch_no = 1

                #looping para ler os arquivos e gerar as NTs
                for i in files:
                    if i == '.DS_Store':
                        pass
                    else:
                        if batch_no == 1:
                            df_exp = pd.read_csv(path+'/'+i, sep=',')
                            batch_no += 1
                        else:
                            df_exp2 = pd.read_csv(path+'/'+i, sep=',')
                            df_exp = pd.concat([df_exp, df_exp2])


                # df_imp = pd.read_csv('IMP_2018-2024.csv', sep=',')
                # df_exp = pd.read_csv('EXP_2018-2024.csv', sep=',')

                #Salvando o último mês
                ultimo_mes = df_imp.query("Ano == @df_imp['Ano'].max()")['Mês'].max()

                #Saber o Mês
                dict_mes = {'1': 'Janeiro', '2': 'Fevereiro', '3': 'Março', '4': 'Abril', '5': 'Maio', '6': 'Junho', '7': 'Julho', '8': 'Agosto', '9': 'Setembro', '10': 'Outubro', '11': 'Novembro', '12': 'Dezembro'}

                #Excluindo os meses
                df_imp.drop(columns=['Mês'], inplace=True)
                df_exp.drop(columns=['Mês'], inplace=True)

                #FUNCAO PARA GERAR AS TABELAS
                def dados(NCM_COD_INT, ano1_INT=2019, ano2_INT=2024):
                # IMPORTAÇÕES

                    df_imp2 = df_imp[(df_imp['NCM']==NCM_COD_INT) & (df_imp['Ano']>=ano1_INT) & (df_imp['Ano']<=ano2_INT)]
                    df_imp3 = df_imp2.groupby(['Ano']).sum()
                    df_imp3.drop(columns=['País'], inplace=True)
                    df_imp3['Preço médio (US$ FOB/Kg)'] = round(df_imp3['Importações (US$ FOB)'] / df_imp3['Importações (Kg)'], 2)
                    df_imp3['NCM'] = str(NCM_COD_INT)


                    df_imp3.insert(2, 'Δ Importações (US$ FOB) (%)', df_imp3['Importações (US$ FOB)'].pct_change().apply(lambda x: '-' if np.isnan(x) else locale.format_string('%.1f%%', x*100, grouping=True)))
                    df_imp3.insert(4, 'Δ Importações (Kg) (%)', df_imp3['Importações (Kg)'].pct_change().apply(lambda x: '-' if np.isnan(x) else locale.format_string('%.1f%%', x*100, grouping=True)))
                    df_imp3.insert(6, 'Δ Preço médio (US$ FOB/Kg) (%)', df_imp3['Preço médio (US$ FOB/Kg)'].pct_change().apply(lambda x: '-' if np.isnan(x) else locale.format_string('%.1f%%', x*100, grouping=True)))

                    
                    df_imp3 = df_imp3.fillna('-')
                    df_imp3.index = df_imp3.index.astype(str)
                    df_imp3['Importações (US$ FOB)'] = df_imp3['Importações (US$ FOB)'].apply(lambda x: locale.format_string("%.2f", x, grouping=True))
                    df_imp3['Importações (Kg)'] = df_imp3['Importações (Kg)'].apply(lambda x: locale.format_string("%.0f", x, grouping=True))

                    # tirar as variações do ano de 2024
                    if ano2_INT == 2024:
                        df_imp3.loc[['2024'], ['Δ Importações (US$ FOB) (%)', 'Δ Importações (Kg) (%)', 'Δ Preço médio (US$ FOB/Kg) (%)']] = '-'

                    # EXPORTAÇÕES

                    df_exp2 = df_exp[(df_exp['NCM']==NCM_COD_INT) & (df_exp['Ano']>=ano1_INT) & (df_exp['Ano']<=ano2_INT)]
                    df_exp3 = df_exp2.groupby(['Ano']).sum()
                    df_exp3.drop(columns=['País'], inplace=True)
                    df_exp3['Preço médio (US$ FOB/Kg)'] = round(df_exp3['Exportações (US$ FOB)'] / df_exp3['Exportações (Kg)'], 2)
                    df_exp3['NCM'] = str(NCM_COD_INT)

                    df_exp3.insert(2, 'Δ Exportações (US$ FOB) (%)', df_exp3['Exportações (US$ FOB)'].pct_change().apply(lambda x: '-' if np.isnan(x) else locale.format_string('%.1f%%', x*100, grouping=True)))
                    df_exp3.insert(4, 'Δ Exportações (Kg) (%)', df_exp3['Exportações (Kg)'].pct_change().apply(lambda x: '-' if np.isnan(x) else locale.format_string('%.1f%%', x*100, grouping=True)))
                    df_exp3.insert(6, 'Δ Preço médio (US$ FOB/Kg) (%)', df_exp3['Preço médio (US$ FOB/Kg)'].pct_change().apply(lambda x: '-' if np.isnan(x) else locale.format_string('%.1f%%', x*100, grouping=True)))


                    df_exp3 = df_exp3.fillna('-')
                    df_exp3.index = df_exp3.index.astype(str)
                    df_exp3['Exportações (US$ FOB)'] = df_exp3['Exportações (US$ FOB)'].apply(lambda x: locale.format_string("%.2f", x, grouping=True))
                    df_exp3['Exportações (Kg)'] = df_exp3['Exportações (Kg)'].apply(lambda x: locale.format_string("%.0f", x, grouping=True))


                    # tirar as variações do ano de 2024
                    if ano2_INT == 2024:
                        df_exp3.loc[['2024'], ['Δ Exportações (US$ FOB) (%)', 'Δ Exportações (Kg) (%)', 'Δ Preço médio (US$ FOB/Kg) (%)']] = '-'


                    # IMPORTAÇÕES POR ORIGEM

                    if ano2_INT == 2024:
                        df_imp_o2 = df_imp[(df_imp['NCM']==NCM_COD_INT) & (df_imp['Ano']==ano2_INT-1)]
                    else:
                        df_imp_o2 = df_imp[(df_imp['NCM']==NCM_COD_INT) & (df_imp['Ano']==ano2_INT)]
                        

                    # df_imp_o2 = df_imp[(df_imp['NCM']==NCM_COD_INT) & (df_imp['Ano']==ano2_INT)]

                    df_imp_o3 = df_imp_o2.groupby(['País']).sum()
                    df_imp_o3.drop(columns=['Ano'], inplace=True)
                    df_imp_o3['Preço médio (US$ FOB/Kg)'] = round(df_imp_o3['Importações (US$ FOB)'] / df_imp_o3['Importações (Kg)'], 2)
                    df_imp_o3['NCM'] = str(NCM_COD_INT)

                    # Convertendo os valores para tipo numérico (float)
                    df_imp_o3['Participação/Total (%)'] = (df_imp_o3['Importações (Kg)'] / df_imp_o2['Importações (Kg)'].sum()) * 100

                    # Formatando os valores como porcentagem com uma casa decimal
                    df_imp_o3['Participação/Total (%)'] = df_imp_o3['Participação/Total (%)'].apply(lambda x: np.nan if np.isnan(x) else round(x, 1))

                    df_imp_o3 = df_imp_o3.fillna('-')
                    df_imp_o3.index = df_imp_o3.index.astype(str)
                    df_imp_o3['Importações (US$ FOB)'] = df_imp_o3['Importações (US$ FOB)'].apply(lambda x: locale.format_string("%.2f", x, grouping=True))
                    df_imp_o3['Importações (Kg)'] = df_imp_o3['Importações (Kg)'].apply(lambda x: locale.format_string("%.0f", x, grouping=True))

                    # df_imp_o3.sort_values(by=['Participação/Total (%)'], ascending=False, inplace=True)
                    df_imp_o3.sort_values(by=['Participação/Total (%)'], ascending=False, inplace=True)

                    if len(df_imp_o3) > 3 and not np.isnan(df_imp_o3['Participação/Total (%)'].iloc[3]):
                        # Calculando a participação de 'outros'
                        outros_participacao =  locale.format_string('%.1f%%', (1 - df_imp_o3['Participação/Total (%)'].iloc[:4].astype(float).sum() / 100)*100, grouping=True)
                    else:
                        outros_participacao = None

                    # Adicionando o símbolo '%' após os valores da coluna 'Participação/Total (%)'
                    df_imp_o3['Participação/Total (%)'] = df_imp_o3['Participação/Total (%)'].astype(str) + '%'
                    df_imp_o3['Participação/Total (%)'] = df_imp_o3['Participação/Total (%)'].apply(lambda x: x.replace('.', ','))

                    #Trocando o . por , nos preços
                    df_exp3['Preço médio (US$ FOB/Kg)'] = df_exp3['Preço médio (US$ FOB/Kg)'].astype(str)
                    df_exp3['Preço médio (US$ FOB/Kg)'] = df_exp3['Preço médio (US$ FOB/Kg)'].apply(lambda x: x.replace('.', ','))
                    df_imp3['Preço médio (US$ FOB/Kg)'] = df_imp3['Preço médio (US$ FOB/Kg)'].astype(str)
                    df_imp3['Preço médio (US$ FOB/Kg)'] = df_imp3['Preço médio (US$ FOB/Kg)'].apply(lambda x: x.replace('.', ','))
                    df_imp_o3['Preço médio (US$ FOB/Kg)'] = df_imp_o3['Preço médio (US$ FOB/Kg)'].astype(str)
                    df_imp_o3['Preço médio (US$ FOB/Kg)'] = df_imp_o3['Preço médio (US$ FOB/Kg)'].apply(lambda x: x.replace('.', ','))

                    #Totais
                    total_imp_kg =  df_imp_o2['Importações (Kg)'].sum()
                    total_imp_vl = df_imp_o2['Importações (US$ FOB)'].sum()
                    if total_imp_kg != 0:
                        total_imp_preco = (round(( total_imp_vl / total_imp_kg ), 2)).astype(str).replace('.',',')
                    else:
                        total_imp_preco = None  # Ou qualquer outro valor que faça sentido para o seu caso

                    return df_imp3, df_exp3, df_imp_o3, outros_participacao, total_imp_kg, total_imp_vl, total_imp_preco


                #Gerar dados
                # df_imp3, df_exp3, df_imp_o3, outros_participacao, total_imp_kg, total_imp_vl, total_imp_preco = dados(df_ncm, ano1_INT, ano2_INT)




                df_imp3, df_exp3, df_imp_o3, outros_participacao, total_imp_kg, total_imp_vl, total_imp_preco = dados(int(df_ncm), ano1_INT, ano2_INT)

                st.subheader(f'Importações - NCM {str(df_ncm3)}')
                st.dataframe(df_imp3)

                st.subheader(f'Exportações - NCM {str(df_ncm3)}')
                st.dataframe(df_exp3)

                if ano2_INT == 2024:
                    st.subheader(f'Importações por origem em {ano2_INT-1} - NCM {df_ncm3}')
                else:
                    st.subheader(f'Importações por origem em {ano2_INT} - NCM {df_ncm3}')

                st.dataframe(df_imp_o3)

                #Generate Doc
                doc = DocxTemplate('Template2.docx')

                # df_ncm2 = str(df_ncm)

                doc.render({
                    "NCM_COD": df_ncm2[0:4]+'.'+df_ncm2[4:6]+'.'+df_ncm2[6:8],
                    "ANO_1": ano1_INT,
                    "ANO_2": ano2_INT,
                    "ANO_3": ano2_INT-1,
                    "df": df_imp3,
                    "df_exp": df_exp3,
                    "df_imp_o": df_imp_o3,
                    "OUTROS": outros_participacao,  
                    "total_imp_kg": locale.format_string("%.0f", total_imp_kg, grouping=True),
                    "total_imp_vl": locale.format_string("%.2f", total_imp_vl, grouping=True),
                    "total_imp_preco": total_imp_preco
                        })

                #Nome do Word
                doc_name = "NCM " + df_ncm2 + ".docx"

                #salvar
                doc.save(doc_name)

                #Dizer o mês
                if ano2_INT == 2024:
                    st.error(f'Atenção: As informações referentes ao ano de 2024 encontram-se atualizadas até o mês de {dict_mes[str(ultimo_mes)]}!', icon="⚠️")

                st.success('Nota Técnica gerada com sucesso! Faça o Download do arquivo:', icon="✅")
                #Exportar o Docx:
                with open(doc_name, 'rb') as f:
                    st.download_button(f'Download (NCM {df_ncm2})', f, file_name=f'NCM {df_ncm2} - Nota Técnica.docx')
                
        







                # def gerarDoc(NCM_COD_C=df_ncm, ano1_INT=2019, ano2_INT=2023):

                #     count = 0
                #     for i in NCM_COD_C:

                #         df_imp3, df_exp3, df_imp_o3, outros_participacao, total_imp_kg, total_imp_vl, total_imp_preco = dados(int(i), ano1_INT, ano2_INT)

                #         #Generate Doc
                #         doc = DocxTemplate('Template2.docx')

                #         doc.render({
                #             "NCM_COD": i[0:4]+'.'+i[4:6]+'.'+i[6:8],
                #             "ANO_1": ano1_INT,
                #             "ANO_2": ano2_INT,
                #             "df": df_imp3,
                #             "df_exp": df_exp3,
                #             "df_imp_o": df_imp_o3,
                #             "OUTROS": outros_participacao,  
                #             "total_imp_kg": locale.format_string("%.0f", total_imp_kg, grouping=True),
                #             "total_imp_vl": locale.format_string("%.2f", total_imp_vl, grouping=True),
                #             "total_imp_preco": total_imp_preco
                #                 })

                #         #Nome do Word
                #         doc_name = "NCM " + i + ".docx"

                #         #salvar
                #         doc.save(doc_name)

                #         st.success('Nota Técnica gerada com sucesso! Faça o Download do arquivo:', icon="✅")
                #         #Exportar o Docx:
                #         with open(doc_name, 'rb') as f:
                #             st.download_button(f'Download (NCM {i})', f, file_name=f'NCM {i} - Nota Técnica.docx', key=i)
                        
                #         count = count + 1

                #     return

                # gerarDoc(NCM_COD_C=df_ncm, ano1_INT=ano1_INT, ano2_INT=ano2_INT)



                
            except:
                st.error('Ops! Algo saiu errado!', icon="🚨")

