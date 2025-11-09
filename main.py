import streamlit as st
from comparar import comparar_pdfs_excel

st.set_page_config(page_title="Comparador de PDFs", layout="wide")

st.title("📄 Comparador de PDFs - Concurso vs Equipamentos")
st.write("Carrega os PDFs do **concurso**, os PDFs dos **equipamentos** e um **TXT com palavras-chave** para comparação.")

# Upload de PDFs
col1, col2, col3 = st.columns(3)
with col1:
    arquivos_concurso = st.file_uploader("📘 Ficheiros do Concurso", type="pdf", accept_multiple_files=True)
with col2:
    arquivos_comparar = st.file_uploader("🧾 Ficheiros de Equipamento", type="pdf", accept_multiple_files=True)
with col3:
    arquivo_txt = st.file_uploader("📝 TXT com Palavras-chave", type="txt", accept_multiple_files=False)

# Botão de execução
if st.button("🔍 Comparar PDFs"):
    if not arquivos_concurso and not arquivo_txt:
        st.error("Por favor, carrega pelo menos um ficheiro do concurso ou um TXT.")
    elif not arquivos_comparar:
        st.error("Por favor, carrega pelo menos um PDF de equipamento.")
    else:
        with st.spinner("A comparar ficheiros... isto pode demorar um pouco ⏳"):
            excel_bytes, df_resultado = comparar_pdfs_excel(arquivos_concurso, arquivos_comparar, arquivo_txt)

        st.success("✅ Comparação concluída com sucesso!")
        st.write("### Resultado da comparação (primeiras linhas):")
        st.dataframe(df_resultado.head(50))

        st.download_button(
            label="📥 Baixar resultado completo em Excel",
            data=excel_bytes,
            file_name="resultado_geral.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
