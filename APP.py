import streamlit as st
import pandas as pd
import yfinance as yf
from ta.momentum import RSIIndicator
from io import StringIO
import requests
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO


def to_excel_download(df, filename='dados.xlsx'):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return output
st.set_page_config(page_title='ATIVOS B3', layout="wide")


def main():
    data_file = st.sidebar.file_uploader("📁Lista de Ativos", type=['xlsx'])
    if data_file is not None:
        st.markdown("<h1 style='text-align: center;'>📊 B3 - Classificador de Ativos</h1>", unsafe_allow_html=True)
        st.markdown("---")
        xls = pd.ExcelFile(data_file)
        abas_disponiveis = xls.sheet_names

        aba_selecionada = st.selectbox("Escolha a aba do Excel", abas_disponiveis)

        @st.cache_data
        def get_atv():
            url = "https://fundamentus.com.br/resultado.php"
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(url, headers=headers)

            df_atv = pd.read_html(StringIO(response.text), decimal=",", thousands=".")[0]

            if isinstance(df_atv.columns, pd.MultiIndex):
                df_atv.columns = df_atv.columns.droplevel()

            df_atv = df_atv.dropna(how='all')
            df_atv['Papel'] = df_atv['Papel'].astype(str) + '.SA'
            return df_atv

        
        def multiselect_filter(df, col, selected):
            if 'all' in selected:
                return df
            return df[df[col].isin(selected)].reset_index(drop=True)

        # Função para filtrar por faixa de RSI
        def rsi_filter(df, faixa):
            return df.query("RSI >= @faixa[0] and RSI <= @faixa[1]").reset_index(drop=True)


        @st.cache_data(show_spinner=False, ttl=21600)
        def baixar_dados_yf(ativo, periodo="60d", intervalo="1d"):
            return yf.download(ativo, period=periodo, interval=intervalo, auto_adjust=True)


        @st.cache_data
        def carregar_ativos(file, aba):
            df = pd.read_excel(file, sheet_name=aba)
            col = df.columns[0]
            df[col] = df[col].astype(str).str.upper() + '.SA'
            return df[col].tolist()
            

        lista_ativos = carregar_ativos(data_file, aba_selecionada)
        st.success(f"✅ {len(lista_ativos)} Ativos foram importados da Aba '{aba_selecionada}'.")

        ordem_hierarquica = {
            "Comprar Agora (Verde -∞|30)": [],
            "Comprar sob Análise (Amarelo 31|35)": [],
            "Atenção para Compra (Vermelho 36|50)": [],
            "Atenção para Venda (Vermelho 51|65)": [],
            "Vender sob Análise (Amarelo 66|70)": [],
            "Vender Agora (Verde 71|+∞)": []
        }

        categorias_compra = [
            "Comprar Agora (Verde -∞|30)",
            "Comprar sob Análise (Amarelo 31|35)",
            "Atenção para Compra (Vermelho 36|50)"
        ]
        categorias_venda = [
            "Atenção para Venda (Vermelho 51|65)",
            "Vender sob Análise (Amarelo 66|70)",
            "Vender Agora (Verde 71|+∞)"
        ]

        st.sidebar.markdown("## 🧠 Classificação Geral")
        filtro = st.sidebar.radio("🔎 Filtrar Seleção Primária:", ["Todos", "Compra", "Venda","Nenhum"])
        st.sidebar.write("----")

        periodo_ifr = 14
        tabela_base = []

        with st.spinner("🔄 Classificando ativos, aguarde..."):
            for ativo in lista_ativos:
                try:
                    df = baixar_dados_yf(ativo)

                    if df.empty or len(df) < periodo_ifr:
                        continue

                    rsi = RSIIndicator(close=df["Close"].squeeze(), window=periodo_ifr)
                    df["RSI"] = rsi.rsi()
                    ifr_atual = df["RSI"].iloc[-1]
                    classificacao_label = ""

                    if ifr_atual <= 30:
                        classificacao_label = "Comprar Agora (Verde -∞|30)"
                    elif 30 < ifr_atual <= 35:
                        classificacao_label = "Comprar sob Análise (Amarelo 31|35)"
                    elif 35 < ifr_atual <= 50:
                        classificacao_label = "Atenção para Compra (Vermelho 36|50)"
                    elif 50 < ifr_atual <= 65:
                        classificacao_label = "Atenção para Venda (Vermelho 51|65)"
                    elif 65 < ifr_atual <= 70:
                        classificacao_label = "Vender sob Análise (Amarelo 66|70)"
                    elif ifr_atual > 70:
                        classificacao_label = "Vender Agora (Verde 71|+∞)"

                    tabela_base.append({
                        "Ativo": ativo,
                        "RSI": round(ifr_atual, 2),
                        "Classificação": classificacao_label
                    })

                except Exception as e:
                    print(f"Erro ao processar {ativo}: {e}")

            # Criar DataFrame base
            df_base = pd.DataFrame(tabela_base)

        st.success(f"✅ {len(df_base)} Ativos carregados com sucesso!")
        st.markdown("<h2 style='text-align: center;'>🧠 Resultado da Classificação Geral dos Ativos</h2>", unsafe_allow_html=True)
        # Aplica filtro se necessário
        if filtro == "Compra":
            df_filtrado = df_base[df_base["Classificação"].isin(categorias_compra)]
        elif filtro == "Venda":
            df_filtrado = df_base[df_base["Classificação"].isin(categorias_venda)]
        elif filtro == "Todos":
            df_filtrado = df_base
        else:  # Nenhum
            df_filtrado = pd.DataFrame()  # vazio


        # Exibir por categoria seguindo a ordem hierárquica
        if not df_filtrado.empty:
            for classe in ordem_hierarquica:
                if classe in df_filtrado["Classificação"].values:
                    subset = df_filtrado[df_filtrado["Classificação"] == classe]
                    st.subheader(f"{classe}")
                    st.dataframe(subset[["Ativo", "RSI"]].reset_index(drop=True))

            # Botão para download de todos os dados filtrados
            excel_data = to_excel_download(df_filtrado)
            st.download_button(
                label="📥 Baixar Classificação Geral em Excel",
                data=excel_data,
                file_name="classificacao_geral.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )        
    
     
        
        else:
            st.warning("⚠️ Nenhum ativo foi classificado com esse filtro.")

        st.write('----')
        

        # ---------------------------
        # FORMULÁRIO DE FILTRO SECUNDÁRIO
        # ---------------------------

        
        with st.sidebar.form(key='filtros_avancados'):
            st.markdown("## 📈 Filtros Avançados")
            # Filtro 1 - Nome dos ativos
            ativos_unicos = sorted(df_base['Ativo'].unique().tolist())
            ativos_unicos.append('all')
            ativos_selecionados = st.multiselect("📌 Ativos específicos:", ativos_unicos, default=['all'])

            # Filtro 2 - Faixa de RSI
            rsi_min = float(df_base["RSI"].min())
            rsi_max = float(df_base["RSI"].max())
            faixa_rsi = st.slider("🟢 Faixa de RSI:", 
                                min_value= rsi_min,
                                max_value= rsi_max,
                                value=(rsi_min, rsi_max),
                                step=1.0)

            # Filtro 3 - Classificação
            classificacoes = df_base['Classificação'].unique().tolist()
            classificacoes.append('all')
            classificacoes_selecionadas = st.multiselect("🏷️ Classificação:", classificacoes, default=['all'])

            aplicar_filtros = st.form_submit_button("✅ Aplicar Filtros")


        # ---------------------------
        # APLICAÇÃO DOS FILTROS COM PIPE
        # ---------------------------
        df_filtrado_secundario = df_base.copy()

        if aplicar_filtros:
            df_filtrado_secundario = (
                df_base
                .pipe(rsi_filter, faixa=faixa_rsi)
                .pipe(multiselect_filter, col='Ativo', selected=ativos_selecionados)
                .pipe(multiselect_filter, col='Classificação', selected=classificacoes_selecionadas)
            )

            
            if not df_filtrado_secundario.empty:
               st.markdown("<h2 style='text-align: center;'>📈 Resultado dos Filtros Avançados</h2>", unsafe_allow_html=True)
               st.markdown("### 🎯 Ativos Filtrados")
               st.dataframe(df_filtrado_secundario.reset_index(drop=True))


            else:
                st.warning("⚠️ Nenhum resultado encontrado com os filtros aplicados.")


        if aplicar_filtros:
            if not df_filtrado_secundario.empty:
                st.markdown("### 📘 Análise Fundamentalista")

                with st.spinner("🔄 Carregando dados da Fundamentus..."):
                    df_atv = get_atv()

                if 'all' not in ativos_selecionados:
                    df_atv_filtrado = multiselect_filter(df_atv, 'Papel', ativos_selecionados)
                    ordem_desejada = ativos_selecionados
                else:
                    ativos_na_planilha = df_base['Ativo'].drop_duplicates().tolist()
                    df_atv_filtrado = multiselect_filter(df_atv, 'Papel', ativos_na_planilha)
                    ordem_desejada = ativos_na_planilha

                # Tratamento para ignorar ativos não encontrados
                df_atv_filtrado = df_atv_filtrado.set_index('Papel')
                ativos_disponiveis = df_atv_filtrado.index.intersection(ordem_desejada)
                ativos_nao_encontrados = list(set(ordem_desejada) - set(ativos_disponiveis))


                # Só exibe se houver dados disponíveis
                if not ativos_disponiveis.empty:
                    df_atv_filtrado = df_atv_filtrado.loc[ativos_disponiveis].reset_index()
                    st.dataframe(df_atv_filtrado.reset_index(drop=True))

                    excel_data_fund = to_excel_download(df_atv_filtrado)
                    st.download_button(
                        label="📥 Baixar Análise Fundamentalista em Excel",
                        data=excel_data_fund,
                        file_name="analise_fundamentalista.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

                if ativos_nao_encontrados:
                    st.warning(f"⚠️ {len(ativos_nao_encontrados)} ativo(os) não encontrado(os) na análise fundamentalista: {', '.join(ativos_nao_encontrados)}")
                    
                else:
                    st.info("ℹ️ Nenhum dado fundamentalista disponível para os demais ativos.")


if __name__ == '__main__':
        main()
