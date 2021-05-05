import fractions

from currency_converter import CurrencyConverter


def fraction_to_decimal(frac: str) -> float:
    frac = frac.strip('"')
    dec = frac.split(' ')[1]
    numerator, denominator = dec.split('/')
    dec = fractions.Fraction(numerator=int(numerator), denominator=int(denominator))

    return float(dec)


def len_to_decimal(value: str) -> float:
    integer = int(value.split(' ')[0].strip('"'))

    if len(value.split(' ')) > 1:
        dec = fraction_to_decimal(value)
    else:
        dec = 0
    return (integer + dec)


def convert_currency(value: float, currency: str, new_currency: str) -> float:
    c = CurrencyConverter()
    return c.convert(amount=value, currency=currency, new_currency=new_currency)


def any_curr(s: str, currency: dict) -> bool:
    return any(c in s for c in currency.keys())


def curr_to_string(curr: str) -> str:
    curr_values = {
        '¥': 'JPY',
        '$': 'USD',
        '€': 'EUR',
        '£': 'GBP'
    }
    if any_curr(curr, curr_values):
        return curr_values.get(curr)
    else:
        raise Exception('Invalid currency.')
