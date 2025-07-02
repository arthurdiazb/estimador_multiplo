import streamlit as st
import pandas as pd
import time

st.set_page_config(
    layout='wide',
    page_title='Trust Partners - H Model')

st.sidebar.markdown('Desenvolvido por Trust Partners')

st.title("Estimador de Valor da Empresa")

CFC = st.number_input("CFC - Estimativa de Média de Conversão de Caixa dos Próximos 3 anos (%) - Fluxo de Caixa Livre / EBITDA") / 100
gP = st.number_input("g2 - Crescimento de Longo Prazo (%)") / 100
r_conservador = st.number_input("WACC Conservador (%)") / 100
r_base = st.number_input("WACC Base (%)") / 100
r_otimista = st.number_input("WACC Otimista (%)") / 100
EBITDA = st.number_input("EBITDA Nominal Atual (R$ '000)")
gR_conservador = st.number_input("Crescimento Conservador (%)") / 100
gR_base = st.number_input("Crescimento Base (%)") / 100
gR_otimista = st.number_input("Crescimento Otimista (%)") / 100

# Parâmetros fixos
periodos_transicao = 7
H = periodos_transicao / 2  # Metade da transição para o H-model

# INPUT: ano para calcular o FCF projetado e o CAGR implícito
ano_cagr = 7  # <-- Você pode mudar para 3, 6, 7 etc.

# Definição dos cenários
cenarios = {
    "Conservador": {"gR": gR_conservador, "r": r_conservador, "CFC": CFC},
    "Base": {"gR": gR_base, "r": r_base, "CFC": CFC},
    "Otimista": {"gR": gR_otimista, "r": r_otimista, "CFC": CFC}
}

gerador = st.button("Gerar Estimativa de Múltiplo")

if gerador:
    resultados = []

    for nome, params in cenarios.items():
        gR = params["gR"]
        r = params["r"]
        CFC = params["CFC"]

        FCF0 = EBITDA * CFC

        # Valor justo (perpetuidade simples ou ajustada)
        if abs(gR - gP) < 1e-6:
            valor_justo = (FCF0 * (1 + gP)) / (r - gP)
        else:
            valor_justo = (FCF0 * (1 + gP)) / (r - gP) + (FCF0 * H * (gR - gP)) / (r - gP)

        # Projeção do FCF até ano_cagr
        fcf = FCF0
        for t in range(1, ano_cagr + 1):
            g_t = gR - ((gR - gP) / periodos_transicao) * (t - 1)
            fcf *= (1 + g_t)
        FCF_n = fcf
        CAGR_n = (FCF_n / FCF0) ** (1 / ano_cagr) - 1

        resultados.append({
            "Cenário": nome,
            "gR": gR,
            "gP": gP,
            "WACC": r,
            "CFC": CFC,
            "Valor Justo (R$ '000)": valor_justo,
            "EV/EBITDA": valor_justo / EBITDA,
            f"FCF_{ano_cagr}": FCF_n,
            f"CAGR_{ano_cagr}a": CAGR_n
        })

    df_resultados = pd.DataFrame(resultados)

    # formatar as colunas de percentual de forma amigável, se quiser
    df_resultados["gR"] = df_resultados["gR"].apply(lambda x: f"{x:.2%}")
    df_resultados["gP"] = df_resultados["gP"].apply(lambda x: f"{x:.2%}")
    df_resultados["CFC"] = df_resultados["CFC"].apply(lambda x: f"{x:.2%}")
    df_resultados["WACC"] = df_resultados["WACC"].apply(lambda x: f"{x:.2%}")
    df_resultados[f"CAGR_{ano_cagr}a"] = df_resultados[f"CAGR_{ano_cagr}a"].apply(lambda x: f"{x:.2%}")
    df_resultados["Valor Justo (R$ '000)"] = df_resultados["Valor Justo (R$ '000)"].apply(lambda x: f"R$ {x:,.2f}")
    df_resultados["EV/EBITDA"] = df_resultados["EV/EBITDA"].apply(lambda x: f"{x:.2f}x")
    df_resultados["FCF_7"] = df_resultados["FCF_7"].apply(lambda x: f"R$ {x:,.2f}")

    st.title("Calculando Múltiplo Resultante...")

    progress_bar = st.progress(0)

    # duração de 3 segundos, atualizando 100 passos
    for percent_complete in range(101):
        progress_bar.progress(percent_complete)
        time.sleep(3 / 100)  # 3 segundos divididos em 100 passos

    st.success("Concluído!")
    st.dataframe(df_resultados, hide_index=True)