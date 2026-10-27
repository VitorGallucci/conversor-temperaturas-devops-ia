"""Regras de conversão, sem arredondamento intermediário."""

import math


def convert(value, source, target):
    """Converte Celsius/Fahrenheit; rejeita valores fisicamente inválidos."""
    if source not in {"C", "F"} or target not in {"C", "F"}:
        raise ValueError("Unidade inválida: use C ou F.")
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("Informe um número válido.")
    try:
        number = float(value)
    except OverflowError as error:
        raise ValueError("Número fora do intervalo suportado.") from error
    if not math.isfinite(number):
        raise ValueError("O valor precisa ser finito.")
    minimum = -273.15 if source == "C" else -459.67
    if number < minimum:
        raise ValueError("Temperatura abaixo do zero absoluto.")
    result = (
        number
        if source == target
        else (number * 1.8 + 32 if source == "C" else (number - 32) / 1.8)
    )
    if not math.isfinite(result):
        raise ValueError("Resultado fora do intervalo suportado.")
    return result
