import functools

RED='\033[0;31m'
GREEN='\033[0;32m'
L_GREEN='\033[1;32m'
ORANGE ='\033[1;33m'
NC='\033[0m' # No Color

fmt_red = f'{RED}{{}}{NC}'
fmt_orange = f'{ORANGE}{{}}{NC}'
fmt_green = f'{GREEN}{{}}{NC}'

print_flushed = functools.partial(print, flush=True)
_print = functools.partial(print, flush=True)

def print_with_color(*a, **k):

    if a and (isinstance(a, str) or isinstance(a[0], str)):
        if a and a[0].startswith('ERROR:'):
            _print(f"{RED}[ERROR]{NC} {a[0].split(':', 1)[1]}" )
        elif a and a[0].startswith('INFO:'):
            _print(f"{GREEN}[INFO]{NC} {a[0].split(':', 1)[1]}" )
        elif a and a[0].startswith('WARNING:'):
            _print(f"{ORANGE}[WARNING]{NC} {a[0].split(':', 1)[1]}" )
        else:
            _print(*a)
    else:
        _print(*a)


