from django.shortcuts import render
from .engine import gerar_diagnostico_basico 


def tela_assistente(request):
    """
    Tela básica do SmartHVAC Assist.
    Por enquanto, só simula uma resposta para termos layout e print.
    """

    # Valores padrão (primeiro acesso / GET)
    resposta_exemplo = None
    sintomas = ""
    marca_equipamento = ""
    tipo_equipamento = "split_hi_wall"
    fluido = "R410A"

    if request.method == "POST":
        sintomas = request.POST.get("sintomas", "")
        marca_equipamento = request.POST.get("marca_equipamento", "")
        tipo_equipamento = request.POST.get("tipo_equipamento", "split_hi_wall")
        fluido = request.POST.get("fluido", "R410A")

        resposta_exemplo = (
            "Exemplo de resposta do SmartHVAC Assist.\n\n"
            "Contexto:\n"
            f"- Marca: {marca_equipamento or 'não informado'}\n"
            f"- Equipamento: {tipo_equipamento or 'não informado'}\n"
            f"- Fluido: {fluido or 'não informado'}\n\n"
            "Possíveis causas:\n"
            "1. Inclinação insuficiente da evaporadora ou bandeja de dreno.\n"
            "2. Excesso de condensação por diferença de temperatura muito alta.\n"
            "3. Entrada de ar falso pelo rasgo da tubulação ou frestas.\n\n"
            "O que verificar:\n"
            "• Conferir inclinação com nível.\n"
            "• Verificar vedação do rasgo da tubulação.\n"
            "• Testar velocidade maior do ventilador e observar o comportamento."
        )

    context = {
        "resposta_exemplo": resposta_exemplo,
        "sintomas": sintomas,
        "marca_equipamento": marca_equipamento,
        "tipo_equipamento": tipo_equipamento,
        "fluido": fluido,
    }
    return render(request, "assistente/tela_assistente.html", context)
