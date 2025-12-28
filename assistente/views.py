from django.shortcuts import render
from .engine_logic import gerar_diagnostico_basico
import os
from openai import OpenAI
from .engine.case_template import CASE_INPUT_TEMPLATE
from .engine.prompt_smarthvac import SMART_HVAC_SYSTEM_PROMPT
from dotenv import load_dotenv
from assistente.engine.memoria import obter_ou_criar_conversa, carregar_historico, salvar_interacao
from assistente.models import ChatConversa
from assistente.engine.base_loader import carregar_base_hvac



load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def tela_assistente(request):
    """
    Tela básica do SmartHVAC Assist.
    """

    resposta_exemplo = None
    sintomas = ""
    marca_equipamento = ""
    tipo_equipamento = "split_hi_wall"
    fluido = "R410A"

    # Garante session_key mesmo para anônimo
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key

    if request.method == "POST":
        acao = request.POST.get("acao", "diagnostico")

        # 🔴 RESET DA CONVERSA
        if acao == "reset":
            ChatConversa.objects.filter(session_key=session_key).delete()

            context = {
                "resposta_exemplo": None,
                "sintomas": "",
                "marca_equipamento": "",
                "tipo_equipamento": "split_hi_wall",
                "fluido": "R410A",
            }
            return render(request, "assistente/tela_assistente.html", context)

        sintomas = request.POST.get("sintomas", "").strip()
        marca_equipamento = request.POST.get("marca_equipamento", "")
        tipo_equipamento = request.POST.get("tipo_equipamento", "split_hi_wall")
        fluido = request.POST.get("fluido", "R410A")

        # 👉 Só chama IA se houver sintomas
        if sintomas:
            if acao == "os":
                pedido_ia = "Gerar resumo técnico profissional para Ordem de Serviço"
            elif acao == "pmoc":
                pedido_ia = "Gerar texto técnico para registro de PMOC"
            else:
                pedido_ia = "Diagnóstico técnico e orientação de testes"

            conteudo = CASE_INPUT_TEMPLATE.format(
                modelo=marca_equipamento or "Não informado",
                tipo=tipo_equipamento or "Não informado",
                fluido=fluido or "Não informado",
                sintomas=sintomas,
                erro="Não informado",
                condicoes="Não informado",
                pedido=pedido_ia
            )
            
            # Carrega contexto da base HVAC
            base_contexto = carregar_base_hvac(
                tipo_equipamento = tipo_equipamento,
                fluido = fluido,
                fabricante = marca_equipamento,
            )    

            try:
                conversa = obter_ou_criar_conversa(session_key)
                historico = carregar_historico(conversa)

                messages = [
                    {"role": "system", "content": SMART_HVAC_SYSTEM_PROMPT}
                ]
                
                if base_contexto:
                    messages.append({
                        'role': 'system',
                        'content': f'BASE TÉCNICA INTERNA:\n{base_contexto}'
                    })
                    
                messages.extend(historico)
                messages.append({"role": "user", "content": conteudo})

                response = client.chat.completions.create(
                    model="gpt-4.1-mini",
                    messages=messages,
                    temperature=0.3
                )

                resposta_exemplo = response.choices[0].message.content

                # salva a interação para memória PRO (48h)
                salvar_interacao(conversa, conteudo, resposta_exemplo)

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
