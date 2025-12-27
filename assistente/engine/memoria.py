from datetime import timedelta
from django.utils import timezone

from assistente.models import ChatConversa, ChatMensagem


TTL_HORAS = 48
MAX_MSGS_PARA_IA = 12  # controla custo/tokens


def _agora():
    return timezone.now()


def _nova_expiracao():
    return _agora() + timedelta(hours=TTL_HORAS)


def obter_ou_criar_conversa(session_key: str) -> ChatConversa:
    # Remove conversas expiradas (MVP: limpeza simples on-demand)
    ChatConversa.objects.filter(expira_em__lt=_agora()).delete()

    conversa = ChatConversa.objects.filter(session_key=session_key, expira_em__gte=_agora()).first()
    if conversa:
        return conversa

    return ChatConversa.objects.create(
        session_key=session_key,
        expira_em=_nova_expiracao(),
    )


def carregar_historico(conversa: ChatConversa) -> list[dict]:
    qs = ChatMensagem.objects.filter(conversa=conversa).order_by("-criado_em")[:MAX_MSGS_PARA_IA]
    msgs = list(reversed(qs))  # volta para ordem cronológica
    return [{"role": m.role, "content": m.content} for m in msgs]


def salvar_interacao(conversa: ChatConversa, user_text: str, assistant_text: str) -> None:
    ChatMensagem.objects.create(conversa=conversa, role="user", content=user_text)
    ChatMensagem.objects.create(conversa=conversa, role="assistant", content=assistant_text)

    # renova a expiração a cada uso (48h a partir da última interação)
    conversa.expira_em = _nova_expiracao()
    conversa.save(update_fields=["expira_em"])
