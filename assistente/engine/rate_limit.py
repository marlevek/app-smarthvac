from django.utils import timezone
from assistente.models import UsoIA
from assistente.engine.permissoes import tem_plano_pro


LIMITE_DIARIO_BASIC = 20
LIMITE_DIARIO_PRO = 80


def limite_diario(usuario):
    return LIMITE_DIARIO_PRO if tem_plano_pro(usuario) else LIMITE_DIARIO_BASIC


def pode_usar_ia(usuario):
    hoje = timezone.now().date()

    uso, _ = UsoIA.objects.get_or_create(
        usuario=usuario,
        data=hoje
    )

    return uso.total_chamadas < limite_diario(usuario)


def registrar_uso(usuario):
    hoje = timezone.now().date()

    uso, _ = UsoIA.objects.get_or_create(
        usuario=usuario,
        data=hoje
    )

    uso.total_chamadas += 1
    uso.save(update_fields=["total_chamadas"])

    return uso.total_chamadas