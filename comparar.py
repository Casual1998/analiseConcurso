import pandas as pd
import io
from pdf_utils import extrair_palavras_pdf_com_posicao

def ler_palavras_txt(arquivo_txt):
    """
    Lê um arquivo TXT e retorna um set com todas as palavras (em lowercase).

    Parâmetros:
        arquivo_txt: arquivo TXT ou objeto upload do Streamlit

    Retorna:
        set de palavras
    """
    palavras = set()
    for linha in arquivo_txt:
        if isinstance(linha, bytes):  # caso venha do Streamlit upload
            linha = linha.decode("utf-8")
        for palavra in linha.lower().split():
            palavra_limpa = palavra.strip(".,;:!?()[]{}\"'")
            if palavra_limpa:
                palavras.add(palavra_limpa)
    return palavras


def comparar_pdfs_excel(arquivos_concurso, arquivos_comparar, arquivo_txt=None):
    """
    Compara os PDFs do concurso e palavras de um TXT com os PDFs de equipamentos
    e gera um Excel em memória indicando palavras em comum e exclusivas.
    Agora as palavras do TXT são corretamente sinalizadas como "Em comum" se aparecerem em qualquer PDF de equipamento.
    """
    # Extrai palavras de todos os PDFs de concurso
    palavras_concurso = []
    for f in arquivos_concurso:
        palavras_concurso.extend(extrair_palavras_pdf_com_posicao(f))
    set_concurso_pdf = set([p["palavra"] for p in palavras_concurso])

    # Extrai palavras do TXT
    set_txt = set()
    if arquivo_txt:
        set_txt = ler_palavras_txt(arquivo_txt)

    # Conjunto completo de palavras "concurso + TXT"
    set_concurso = set_concurso_pdf | set_txt

    dados_excel = []

    for ficheiro in arquivos_comparar:
        nome_arquivo = ficheiro.name
        palavras_equipamento = extrair_palavras_pdf_com_posicao(ficheiro)
        lista_equipamento = [p["palavra"] for p in palavras_equipamento]

        # Itera sobre todas as palavras do PDF de equipamento
        for ocorrencia_equip in palavras_equipamento:
            palavra = ocorrencia_equip["palavra"]
            if palavra in set_concurso:
                status = "Em comum"
            else:
                status = "Apenas no equipamento"
            dados_excel.append({
                "PDF_Equipamento": nome_arquivo,
                "Palavra": palavra,
                "Status": status,
                "Página": ocorrencia_equip["pagina"],
                "Linha": ocorrencia_equip["linha"]
            })

        # Agora verifica palavras do TXT que não apareceram neste PDF
        for palavra_txt in set_txt:
            if palavra_txt not in lista_equipamento:
                # Palavras do TXT sem ocorrência no PDF
                dados_excel.append({
                    "PDF_Equipamento": nome_arquivo,
                    "Palavra": palavra_txt,
                    "Status": "Apenas no TXT",
                    "Página": None,
                    "Linha": None
                })

        # Verifica palavras de concurso que não aparecem no equipamento
        for palavra_pdf in set_concurso_pdf:
            if palavra_pdf not in lista_equipamento:
                ocorrencia_concurso = next((p for p in palavras_concurso if p["palavra"] == palavra_pdf), {"pagina": None, "linha": None})
                dados_excel.append({
                    "PDF_Equipamento": nome_arquivo,
                    "Palavra": palavra_pdf,
                    "Status": "Apenas no concurso",
                    "Página": ocorrencia_concurso["pagina"],
                    "Linha": ocorrencia_concurso["linha"]
                })

    df = pd.DataFrame(dados_excel)
    output = io.BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)
    return output, df


    # Cria o Excel em memória
    df = pd.DataFrame(dados_excel)
    output = io.BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)
    return output, df
