import pdfplumber

def extrair_palavras_pdf_com_posicao(arquivo):
    """
    Extrai todas as palavras de um PDF com suas posições (página e linha).

    Parâmetros:
        arquivo: arquivo PDF ou objeto de upload do Streamlit

    Retorna:
        lista de dicionários: [{"palavra": str, "pagina": int, "linha": int}, ...]
    """
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
