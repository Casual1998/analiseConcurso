import streamlit as st
import pdfplumber
import pandas as pd
import io

# === FUNÇÃO PARA EXTRAIR PALAVRAS COM POSIÇÃO ===
def extrair_palavras_pdf_com_posicao(arquivo):
    palavras = []
    with pdfplumber.open(arquivo) as pdf:
        for num_pagina, pagina in enumerate(pdf.pages, start=1):
            texto = pagina.extract_text()
            if texto:
                linhas = texto.split("\n")
                for num_linha, linha in enumerate(linhas, start=1):
                    for palavra in linha.lower().split():
                        palavra_limpa = palavra.strip(".,;:!?()[]{}\"'")
                        if palavra_limpa:
                            palavras.append({
                                "palavra": palavra_limpa,
                                "pagina": num_pagina,
                                "linha": num_linha
                            })
    return palavras


# === COMPARAR PDFs E GERAR EXCEL EM MEMÓRIA ===
def comparar_pdfs_excel(arquivos_concurso, arquivos_comparar):
    # Extrai palavras de todos os PDFs de concurso
    palavras_concurso = []
    for f in arquivos_concurso:
        palavras_concurso.extend(extrair_palavras_pdf_com_posicao(f))
    set_concurso = set([p["palavra"] for p in palavras_concurso])

    dados_excel = []

    for ficheiro in arquivos_comparar:
        nome_arquivo = ficheiro.name
        palavras_equipamento = extrair_palavras_pdf_com_posicao(ficheiro)
        set_equipamento = set([p["palavra"] for p in palavras_equipamento])

        em_comum = set_equipamento & set_concurso
        apenas_equipamento = set_equipamento - set_concurso
        apenas_concurso = set_concurso - set_equipamento

        # Em comum
        for palavra in em_comum:
            ocorrencia_equip = next(p for p in palavras_equipamento if p["palavra"] == palavra)
            dados_excel.append({
                "PDF_Equipamento": nome_arquivo,
                "Palavra": palavra,
                "Status": "Em comum",
                "Página": ocorrencia_equip["pagina"],
                "Linha": ocorrencia_equip["linha"]
            })

        # Apenas no equipamento
        for palavra in apenas_equipamento:
            ocorrencia_equip = next(p for p in palavras_equipamento if p["palavra"] == palavra)
            dados_excel.append({
                "PDF_Equipamento": nome_arquivo,
                "Palavra": palavra,
                "Status": "Apenas no equipamento",
                "Página": ocorrencia_equip["pagina"],
                "Linha": ocorrencia_equip["linha"]
            })

        # Apenas no concurso
        for palavra in apenas_concurso:
            ocorrencia_concurso = next(p for p in palavras_concurso if p["palavra"] == palavra)
            dados_excel.append({
                "PDF_Equipamento": nome_arquivo,
                "Palavra": palavra,
                "Status": "Apenas no concurso",
                "Página": ocorrencia_concurso["pagina"],
                "Linha": ocorrencia_concurso["linha"]
            })

    # Cria o Excel em memória
    df = pd.DataFrame(dados_excel)
    output = io.BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)
    return output, df


# === INTERFACE STREAMLIT ===
st.set_page_config(page_title="Comparador de PDFs", layout="wide")

st.title("📄 Comparador de PDFs - Concurso vs Equipamentos")
st.write("Carrega os PDFs do **concurso** e os PDFs dos **equipamentos** para comparar as palavras em comum e exclusivas.")

# Upload de PDFs
col1, col2 = st.columns(2)
with col1:
    arquivos_concurso = st.file_uploader("📘 Ficheiros do Concurso", type="pdf", accept_multiple_files=True)
with col2:
    arquivos_comparar = st.file_uploader("🧾 Ficheiros de Equipamento", type="pdf", accept_multiple_files=True)

# Botão de execução
if st.button("🔍 Comparar PDFs"):
    if not arquivos_concurso or not arquivos_comparar:
        st.error("Por favor, carrega pelo menos um ficheiro em cada categoria.")
    else:
        with st.spinner("A comparar ficheiros... isto pode demorar um pouco ⏳"):
            excel_bytes, df_resultado = comparar_pdfs_excel(arquivos_concurso, arquivos_comparar)

        st.success("✅ Comparação concluída com sucesso!")
        st.write("### Resultado da comparação (primeiras linhas):")
        st.dataframe(df_resultado.head(50))

        st.download_button(
            label="📥 Baixar resultado completo em Excel",
            data=excel_bytes,
            file_name="resultado_geral.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
