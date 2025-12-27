from django.shortcuts import render
from .engine_logic import gerar_diagnostico_basico
import os
from openai import OpenAI
from .engine.case_template import CASE_INPUT_TEMPLATE
from .engine.prompt_smarthvac import SMART_HVAC_SYSTEM_PROMPT
from dotenv import load_dotenv


load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


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
        sintomas = request.POST.get("sintomas", "").strip()
        marca_equipamento = request.POST.get("marca_equipamento", "")
        tipo_equipamento = request.POST.get(
            "tipo_equipamento", "split_hi_wall")
        fluido = request.POST.get("fluido", "R410A")
        acao = request.POST.get('acao', 'diagnostico')

    pedido_ia = 'Diagnóstico técnico e orientação de testes'

    # Monta o caso técnico para a IA
    if sintomas:
        if acao == 'os':
            pedido_ia = 'Gerar resumo técninco profissional para Ordem de Serviço'

    elif acao == 'pmoc':
        pedido_ia = 'Gerar texto técnico para registro de PMOC'

    conteudo = CASE_INPUT_TEMPLATE.format(
        modelo=marca_equipamento or "Não informado",
        tipo=tipo_equipamento or "Não informado",
        fluido=fluido or "Não informado",
        sintomas=sintomas or "Não informado",
        erro="Não informado",
        condicoes="Não informado",
        pedido=pedido_ia
    )

    messages = [
        {"role": "system", "content": SMART_HVAC_SYSTEM_PROMPT},
        {"role": "user", "content": conteudo}
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=messages,
            temperature=0.3
        )

        resposta_exemplo = response.choices[0].message.content

    except Exception as e:
        resposta_exemplo = f"Erro ao consultar o SmartHVAC Assist: {str(e)}"

    context = {
        "resposta_exemplo": resposta_exemplo,
        "sintomas": sintomas,
        "marca_equipamento": marca_equipamento,
        "tipo_equipamento": tipo_equipamento,
        "fluido": fluido,
    }


    return render(request, "assistente/tela_assistente.html", context)
