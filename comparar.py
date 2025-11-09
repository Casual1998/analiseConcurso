import pandas as pd
import io
from pdf_utils import extrair_palavras_pdf_com_posicao

def ler_palavras_txt(arquivo_txt):
    """
    Lê um arquivo TXT e retorna um set com todas as palavras (em lowercase).
    """
    palavras = set()
    for linha in arquivo_txt:
        if isinstance(linha, bytes):
            linha = linha.decode("utf-8")
        for palavra in linha.lower().split():
            palavra_limpa = palavra.strip(".,;:!?()[]{}\"'")
            if palavra_limpa:
                palavras.add(palavra_limpa)
    return palavras

def comparar_pdfs_excel(arquivos_concurso, arquivos_comparar, arquivo_txt=None):
    """
    Compara os PDFs do concurso e/ou palavras de um TXT com os PDFs de equipamentos
    e gera um Excel em memória indicando palavras em comum, exclusivas ou em todos os equipamentos.
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

    # Cria um dicionário para contar em quantos arquivos cada palavra aparece
    contador_palavras = {}

    # Primeiro, percorre todos os PDFs de equipamentos
    for ficheiro in arquivos_comparar:
        nome_arquivo = ficheiro.name
        palavras_equipamento = extrair_palavras_pdf_com_posicao(ficheiro)
        set_equipamento = set([p["palavra"] for p in palavras_equipamento])

        # Contagem de palavras por arquivo
        for palavra in set_equipamento:
            contador_palavras[palavra] = contador_palavras.get(palavra, 0) + 1

        # Apenas para registro individual
        for palavra in set_equipamento:
            ocorrencia_equip = next(p for p in palavras_equipamento if p["palavra"] == palavra)
            dados_excel.append({
                "PDF_Equipamento": nome_arquivo,
                "Palavra": palavra,
                "Status": "",  # Será preenchido depois
                "Página": ocorrencia_equip["pagina"],
                "Linha": ocorrencia_equip["linha"]
            })

    # Processa palavras para atualizar status
    total_equipamentos = len(arquivos_comparar)
    for row in dados_excel:
        palavra = row["Palavra"]
        if palavra in set_concurso and contador_palavras[palavra] == total_equipamentos:
            row["Status"] = "Em todos os equipamentos e concurso/TXT"
        elif palavra in set_concurso:
            row["Status"] = "Em comum"
        elif contador_palavras[palavra] == total_equipamentos:
            row["Status"] = "Em todos os equipamentos"
        else:
            row["Status"] = "Apenas no equipamento"

    # Adiciona palavras que estão apenas no concurso/TXT e não aparecem em nenhum equipamento
    palavras_apenas_concurso = set_concurso - set(contador_palavras.keys())
    for palavra in palavras_apenas_concurso:
        ocorrencia_concurso = next((p for p in palavras_concurso if p["palavra"] == palavra), {"pagina": None, "linha": None})
        dados_excel.append({
            "PDF_Equipamento": "-",
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
