# assistente/engine.py

def gerar_diagnostico_basico(
    sintomas: str,
    marca_equipamento: str,
    tipo_equipamento: str,
    fluido: str,
) -> str:
    """
    Gera um diagnóstico de exemplo baseado em regras simples.
    Isso é só o "motor" do MVP sem IA.
    """

    sintomas_lower = (sintomas or "").lower()

    # Cabeçalho comum com contexto
    cabecalho = (
        "Exemplo de resposta do SmartHVAC Assist.\n\n"
        "Contexto informado:\n"
        f"- Marca: {marca_equipamento or 'não informado'}\n"
        f"- Tipo de equipamento: {tipo_equipamento or 'não informado'}\n"
        f"- Fluido: {fluido or 'não informado'}\n\n"
    )

    # Caso 1 – Evaporadora pingando / vazando água
    if any(palavra in sintomas_lower for palavra in ["pinga", "pingando", "vazando água", "vazando agua"]):
        corpo = (
            "Possíveis causas (evaporadora pingando):\n"
            "1. Bandeja de dreno desnivelada ou obstruída.\n"
            "2. Mangueira de dreno estrangulada ou com sifão invertido.\n"
            "3. Excesso de condensação por diferença de temperatura muito alta.\n"
            "4. Entrada de ar falso pelo rasgo da tubulação ou frestas na parede.\n\n"
            "Passos recomendados para verificação:\n"
            "• Conferir inclinação da evaporadora e da bandeja com nível.\n"
            "• Desconectar e testar escoamento da mangueira de dreno.\n"
            "• Verificar vedação do rasgo da tubulação (massa, espuma, etc.).\n"
            "• Observar se a bandeja enche rápido demais em operação contínua.\n"
        )
        return cabecalho + corpo

    # Caso 2 – Freezer / câmara não atinge temperatura (ex.: -28°C)
    if any(p in sintomas_lower for p in ["não atinge", "nao atinge", "-28", "não chega", "nao chega", "temperatura alta"]):
        corpo = (
            "Possíveis causas (freezer/câmara não atingindo temperatura):\n"
            "1. Carga de fluido refrigerante baixa ou excesso de fluido.\n"
            "2. Sujeira em condensador (ar ou água) prejudicando a troca térmica.\n"
            "3. Isolamento térmico comprometido (borracha de porta, frestas, etc.).\n"
            "4. Termostato/controlador desajustado ou com histerese inadequada.\n\n"
            "Passos recomendados para verificação:\n"
            "• Verificar pressão de sucção e descarga e comparar com tabela do fluido.\n"
            "• Inspecionar condensador e ventiladores (limpeza e rotação).\n"
            "• Conferir vedação da porta e presença de gelo em excesso no evaporador.\n"
            "• Verificar setpoint e histerese no controlador eletrônico.\n"
        )
        return cabecalho + corpo

    # Caso 3 – Não gela / baixa capacidade em split
    if any(p in sintomas_lower for p in ["não gela", "nao gela", "fraco", "pouco frio"]):
        corpo = (
            "Possíveis causas (baixa capacidade de refrigeração):\n"
            "1. Filtro de ar sujo ou evaporadora muito suja.\n"
            "2. Condensadora obstruída ou com ventilação inadequada.\n"
            "3. Carga de fluido fora do ideal (baixa ou alta).\n"
            "4. Dimensionamento inadequado para o ambiente (BTUs insuficientes).\n\n"
            "Passos recomendados para verificação:\n"
            "• Verificar limpeza de filtros e serpentina da evaporadora.\n"
            "• Conferir se há obstruções no fluxo de ar da condensadora.\n"
            "• Medir pressões e temperaturas, comparando com tabela do fluido.\n"
            "• Confirmar carga térmica do ambiente versus capacidade do equipamento.\n"
        )
        return cabecalho + corpo

    # Caso padrão (fallback)
    corpo = (
        "No momento, não encontrei um padrão claro pelos sintomas informados.\n\n"
        "Sugestão de próximos passos:\n"
        "1. Detalhe melhor os sintomas (tempo de funcionamento, ruídos, pressões, temperaturas).\n"
        "2. Informe se o problema é intermitente ou constante.\n"
        "3. Quando possível, registre:\n"
        "   • Pressão de sucção e descarga.\n"
        "   • Temperatura de retorno e de insuflamento.\n"
        "   • Corrente do compressor.\n\n"
        "Com mais detalhes, o SmartHVAC Assist poderá sugerir um caminho mais específico de diagnóstico.\n"
    )
    return cabecalho + corpo
