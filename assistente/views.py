from django.shortcuts import render, redirect
from .engine_logic import gerar_diagnostico_basico
import os
from openai import OpenAI
from .engine.case_template import CASE_INPUT_TEMPLATE
from .engine.prompt_smarthvac import SMART_HVAC_SYSTEM_PROMPT
from dotenv import load_dotenv
from assistente.engine.memoria import obter_ou_criar_conversa, carregar_historico, salvar_interacao
from assistente.models import ChatConversa
from assistente.engine.base_loader import carregar_base_hvac
from assistente.engine.acesso  import usuario_autorizado
from assistente.engine.rate_limit import pode_usar_ia, registrar_uso
from assistente.engine.permissoes import tem_plano_pro
from django.utils import timezone
from assistente.models import UsoIA
from assistente.engine.prompt_smarthvac import (
    SMART_HVAC_SYSTEM_PROMPT,
    PROMPT_MODO_BASIC,
    PROMPT_MODO_PRO,
)


load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def tela_assistente(request):
    """
    Tela básica do SmartHVAC Assist.
    """

    # ===============================
    # AUTENTICAÇÃO / AUTORIZAÇÃO
    # ===============================
    if not request.user.is_authenticated:
        return redirect('/admin/login')

    if not usuario_autorizado(request.user):
        return render(request, 'assistente/acesso_bloqueado.html')

    # ===============================
    # PLANO / MEMÓRIA / LIMITES
    # ===============================
    plano = request.user.perfil.plano if hasattr(request.user, 'perfil') else 'basic'
    memoria_ativa = (plano == 'pro')

    limite_hoje = 80 if memoria_ativa else 20

    hoje = timezone.now().date()
    uso_hoje = UsoIA.objects.filter(usuario=request.user, data=hoje).first()
    usos_hoje = uso_hoje.total_chamadas if uso_hoje else 0

    # ===============================
    # ESTADO INICIAL
    # ===============================
    resposta_exemplo = None
    sintomas = ""
    marca_equipamento = ""
    tipo_equipamento = "split_hi_wall"
    fluido = "R410A"

    # session_key (memória)
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key

    # ===============================
    # POST
    # ===============================
    if request.method == "POST":
        acao = request.POST.get("acao", "diagnostico")

        # 🔴 RESET
        if acao == "reset":
            ChatConversa.objects.filter(session_key=session_key).delete()
            return render(request, "assistente/tela_assistente.html", {
                "plano": plano,
                "memoria_ativa": memoria_ativa,
                "usos_hoje": usos_hoje,
                "limite_hoje": limite_hoje,
            })

        # 🔒 BLOQUEIO PRO
        if acao in ["os", "pmoc"] and not memoria_ativa:
            resposta_exemplo = (
                "🔒 Este recurso está disponível apenas no plano PRO.\n\n"
                "Faça upgrade para liberar copiar para OS e PMOC."
            )
            return render(request, "assistente/tela_assistente.html", {
                "resposta_exemplo": resposta_exemplo,
                "plano": plano,
                "memoria_ativa": memoria_ativa,
                "usos_hoje": usos_hoje,
                "limite_hoje": limite_hoje,
            })

        sintomas = request.POST.get("sintomas", "").strip()
        marca_equipamento = request.POST.get("marca_equipamento", "")
        tipo_equipamento = request.POST.get("tipo_equipamento", "split_hi_wall")
        fluido = request.POST.get("fluido", "R410A")

        # ⛔ RATE LIMIT
        if usos_hoje >= limite_hoje:
            resposta_exemplo = (
                "⚠️ Limite diário de uso atingido.\n\n"
                "Você pode continuar amanhã ou fazer upgrade de plano."
            )
            return render(request, "assistente/tela_assistente.html", {
                "resposta_exemplo": resposta_exemplo,
                "plano": plano,
                "memoria_ativa": memoria_ativa,
                "usos_hoje": usos_hoje,
                "limite_hoje": limite_hoje,
            })

        # ===============================
        # CHAMADA IA
        # ===============================
        if sintomas:
            if acao == "os":
                pedido_ia = "Gerar texto profissional para Ordem de Serviço"
            elif acao == "pmoc":
                pedido_ia = "Gerar texto técnico para observações de PMOC"
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

            base_contexto = carregar_base_hvac(
                tipo_equipamento=tipo_equipamento,
                fluido=fluido,
                fabricante=marca_equipamento,
            )

            try:
                historico = []
                if memoria_ativa:
                    conversa = obter_ou_criar_conversa(session_key)
                    historico = carregar_historico(conversa)

                modo_prompt = PROMPT_MODO_PRO if memoria_ativa else PROMPT_MODO_BASIC

                messages = [
                    {"role": "system", "content": SMART_HVAC_SYSTEM_PROMPT},
                    {"role": "system", "content": modo_prompt},
                ]

                if base_contexto:
                    messages.append({
                        "role": "system",
                        "content": f"BASE TÉCNICA INTERNA:\n{base_contexto}"
                    })

                messages.extend(historico)
                messages.append({"role": "user", "content": conteudo})

                response = client.chat.completions.create(
                    model="gpt-4.1-mini",
                    messages=messages,
                    temperature=0.3
                )

                resposta_exemplo = response.choices[0].message.content

                registrar_uso(request.user)

                if memoria_ativa:
                    salvar_interacao(conversa, conteudo, resposta_exemplo)

            except Exception as e:
                resposta_exemplo = f"Erro ao consultar o SmartHVAC Assist: {str(e)}"

    # ===============================
    # CONTEXTO FINAL
    # ===============================
    context = {
        "resposta_exemplo": resposta_exemplo,
        "sintomas": sintomas,
        "marca_equipamento": marca_equipamento,
        "tipo_equipamento": tipo_equipamento,
        "fluido": fluido,
        "plano": plano,
        "memoria_ativa": memoria_ativa,
        "usos_hoje": usos_hoje,
        "limite_hoje": limite_hoje,
    }

    return render(request, "assistente/tela_assistente.html", context)
