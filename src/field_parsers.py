"""Utility parser functions to extract stuff."""
import re

not_amount_pattern = re.compile(r'[^0-9\,\.\-]+')
not_digits_pattern = re.compile(r'[^0-9]+')

def parse_amount(string):
    digits = re.sub(not_digits_pattern, '', string)
    
    if len(digits) == 0:
        return -1

    supposed_amount = re.sub(not_amount_pattern, '', string)

    # dirty fix for seedrs.com
    if supposed_amount[0] == ".":
        supposed_amount = supposed_amount[1:]

    dot_count = supposed_amount.count(".")
    comma_count = supposed_amount.count(",")
    
    # special case of 0.91.- CHF - who even does this? :)
    if len(supposed_amount) >= 2 and supposed_amount[-1] == "-" and supposed_amount[-2] == ".":
        return float(supposed_amount[:-2])
    
    supposed_amount.replace("-", "")

    if dot_count == 1 and comma_count == 0:
        
        if len(supposed_amount.split(".")[-1]) == 2:
            return float(supposed_amount)
        
        return float(supposed_amount.replace(".", ""))

    if dot_count == 0 and comma_count == 1:
        
        if len(supposed_amount.split(",")[-1]) == 2:
            return float(supposed_amount.replace(",", "."))
        
        return float(supposed_amount.replace(",", ""))

    if dot_count == 1 and comma_count == 1:
        rev = supposed_amount[::-1]  
        if rev.index(",") > rev.index("."):
            # , is before .
            return float(supposed_amount.replace(",", ""))
        return float(supposed_amount.replace(".", "").replace(",", "."))

    if dot_count > 1:
        return float(supposed_amount.replace(".", "").replace(",", "."))
    
    if comma_count > 1:
        return float(supposed_amount.replace(",", ""))

    return float(supposed_amount)


def parse_currency(string):
    string = string.lower()
    if "€" in string or "euro" in string or "eur" in string:
        return "EUR"

    if "£" in string or "pound" in string or "gbp" in string:
        return "GBP"

    if "$" in string or "dollar" in string or "usd" in string:
        return "USD"

    if "fr" in string or "chf" in string:
        return "CHF"
    
    return ""

def parse_amount_and_currency(string):
    return parse_amount(string), parse_currency(string)


if __name__ == "__main__":

    test_cases = [
        ("€0.31", 0.31, "EUR"),
        ("€396,000", 396000, "EUR"),
        ("€328,145", 328145, "EUR"),
        ("€20.15", 20.15, "EUR"),
        ("€25,000.00", 25000.00, "EUR"),
        ("€5.4M", 5400000, "EUR"),
        ("€1.3Bn", 1300000000, "EUR"),
        ("€450k", 450000, "EUR"),
        ("£8.3M", 8300000, "GBP"),
        ("£339,020", 339020, "GBP"),
        ("£450,001", 450001, "GBP"),
        ("£3.07", 3.07, "GBP"),
        ("£21.49", 21.49, "GBP"),
        ("min. £21.49 +", 21.49, "GBP"),
        ("£50,000,122,122.00", 50000122122.00, "GBP"),
        ("3.192.250 EUR", 3192250, "EUR"),
        ("500 Euro", 500, "EUR"),
        ("1.000 Euro", 1000, "EUR"),
        ("190.000 EUR", 190000, "EUR"),
        ("100.000  CHF", 100000, "CHF"),
        ("500.000  CHF", 500000, "CHF"),
        ("0,91   CHF", 0.91, "CHF"),
        ("151.949 CHF", 151949, "CHF"),
        ("200.000  CHF", 200000, "CHF"),
        ("2.000.000  CHF", 2000000, "CHF"),
        ("250.000  CHF", 250000, "CHF"),
        ("350.000  €", 350000, "EUR"),
        ("108.900 €", 108900, "EUR"),
        ("CHF 273.- ", 273, "CHF"),
        ("CHF 0.91.-", 0.91, "CHF"),
        ("CHF 50’000.-", 50000, "CHF"),
        ("546 CHF", 546, "CHF"),
        ("1.001 CHF", 1001, "CHF"),
        ("", -1, ""),
        (".", -1, ""),
        (".-", -1, ""),
        ("-.", -1, ""),
        ("-.fasdfasdf asdf asdf asdf .[z,wxxx]", -1, ""),
    ]

    failed = 0
    for string, expected_result, expected_currency in test_cases:
        guess_result, guess_currency = parse_amount_and_currency(string)
        if guess_result == expected_result and guess_currency == expected_currency:
            continue

        failed += 1
        print(f"FAILED: for \"{string}\" got {(guess_result, guess_currency)} but expected {(expected_result, expected_currency)}.")

    if failed == 0:
        print("PASSED all test: parse_amount_and_currency().")
    else:
        print(f"FAILED {failed}/{len(test_cases)} tests: parse_amount_and_currency().")
