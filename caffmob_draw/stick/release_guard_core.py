"""Regra pura de supressão do ímã após desgrudar manualmente (feature 021, T016; RF-09, RN-08).

Impede o ciclo infinito onde desgrudar um armário e movê-lo poucos centímetros para frente (ainda dentro da tolerância
do ímã) faz o `settle` puxá-lo de volta para o mesmo hospedeiro.
"""

HYSTERESIS_MARGIN_M = 0.10  # 100 mm além da tolerância do ímã para liberar o mesmo hospedeiro novamente


def should_suppress_magnet(
    released_host_name: str,
    candidate_host_name: str,
    distance_m: float,
    magnet_tolerance_m: float = 0.05,
) -> bool:
    """Retorna True se o ímã deve ignorar `candidate_host_name` porque o item acabou de ser desgrudado dele."""
    if not released_host_name or not candidate_host_name:
        return False
    if released_host_name != candidate_host_name:
        return False
    return float(distance_m) <= (float(magnet_tolerance_m) + HYSTERESIS_MARGIN_M)


def should_clear_release_guard(
    released_host_name: str,
    min_distance_to_released_host_m: float,
    magnet_tolerance_m: float = 0.05,
) -> bool:
    """Retorna True quando o item já se afastou além da zona de histerese e o guarda pode ser limpo."""
    if not released_host_name:
        return False
    return float(min_distance_to_released_host_m) > (float(magnet_tolerance_m) + HYSTERESIS_MARGIN_M)
