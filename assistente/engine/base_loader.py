import os 


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
BASE_HVAC_DIR = os.path.join(BASE_DIR, 'base_hvac')


def ler_arquivo_md(caminho):
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return ""
    

def carregar_base_hvac(tipo_equipamento, fluido=None, fabricante=None):
    '''
    Docstring para carregar_baser_hvac
    Carrega os trechos relevantes da base HVAC
    com base no tipo de equipamento.
    '''
    partes = []
    
    # Base por tipo de equipamento
    pasta_tipo = os.path.join(BASE_HVAC_DIR, tipo_equipamento)
    if os.path.isdir(pasta_tipo):
        for nome in ['sintomas.md', 'causas_comuns.md', 'testes_e_medicoes.md', 'alertas.md']:
            caminho = os.path.join(pasta_tipo, nome)
            texto = ler_arquivo_md(caminho)
            if texto:
                partes.append(texto)
    
    # Variações por fluido
    if fluido:
        texto = ler_arquivo_md(os.path.join(BASE_HVAC_DIR, 'variacoes_por_fluido.md'))
        if texto:
            partes.append(texto)
            
    # Variações por fabricante
    if fabricante:
        texto = ler_arquivo_md(os.path.join(BASE_HVAC_DIR, 'variacoes_por_fabricante.md'))
        if texto:
            partes.append(texto)
        
    return '\n\n'.join(partes)

