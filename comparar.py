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
    Compara os PDFs do concurso e/ou palavras de um TXT com os PDFs de equipamentos
    e gera um Excel em memória indicando palavras em comum e exclusivas.
    Cada ocorrência em cada PDF de equipamento será registrada separadamente.

    Parâmetros:
        arquivos_concurso: lista de PDFs do concurso
        arquivos_comparar: lista de PDFs de equipamentos
        arquivo_txt: arquivo TXT opcional com palavras-chave

    Retorna:
        output: BytesIO do Excel gerado
        df: DataFrame com os resultados
    """
    # Extrai palavras de todos os PDFs de concurso
    palavras_concurso = []
    for f in arquivos_concurso:
        palavras_concurso.extend(extrair_palavras_pdf_com_posicao(f))
    set_concurso = set([p["palavra"] for p in palavras_concurso])

    # Se houver TXT, adiciona as palavras dele ao conjunto
    if arquivo_txt:
        palavras_txt = ler_palavras_txt(arquivo_txt)
        set_concurso.update(palavras_txt)

    dados_excel = []

    # Itera sobre todos os PDFs de equipamento
    for ficheiro in arquivos_comparar:
        nome_arquivo = ficheiro.name
        palavras_equipamento = extrair_palavras_pdf_com_posicao(ficheiro)

        # Cria lista de palavras em equipamento
        lista_equipamento = [p["palavra"] for p in palavras_equipamento]

        # Percorre todas as palavras do equipamento e marca o status
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

        # Adiciona palavras do concurso/TXT que não apareceram no PDF de equipamento
        for palavra in set_concurso:
            if palavra not in lista_equipamento:
                ocorrencia_concurso = next((p for p in palavras_concurso if p["palavra"] == palavra), {"pagina": None, "linha": None})
                dados_excel.append({
                    "PDF_Equipamento": nome_arquivo,
                    "Palavra": palavra,
                    "Status": "Apenas no concurso/TXT",
                    "Página": ocorrencia_concurso["pagina"],
                    "Linha": ocorrencia_concurso["linha"]
                })

    # Cria o Excel em memória
    df = pd.DataFrame(dados_excel)
    output = io.BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)
    return output, df
