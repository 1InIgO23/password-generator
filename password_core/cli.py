"""Command-line interface for password_core.

Examples:
    python -m password_core password --length 20 --symbols
    python -m password_core passphrase --words 5 --capitalize --number
    python -m password_core password --count 3 --entropy

The CLI only translates command-line arguments into Options /
PassphraseOptions and calls the core. It does not generate anything itself.
"""

from __future__ import annotations

import argparse
import sys

from .generator import Options, generate_password, pool_size
from .passphrase import PassphraseOptions, generate_passphrase, passphrase_entropy_bits
from .strength import entropy_bits, strength_label

MAX_COUNT = 100


def _count(value: str) -> int:
    """argparse `type` for --count: an integer between 1 and MAX_COUNT."""
    try:
        n = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"'{value}' is not an integer")
    if not 1 <= n <= MAX_COUNT:
        raise argparse.ArgumentTypeError(f"must be between 1 and {MAX_COUNT}")
    return n


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="password_core",
        description="Secure password and passphrase generator.",
    )

    # Options shared by both subcommands live in a "parent" parser,
    # so they are defined once and inherited by each subcommand.
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "-c", "--count", type=_count, default=1,
        help=f"how many to generate (1-{MAX_COUNT}, default 1)",
    )
    common.add_argument(
        "-e", "--entropy", action="store_true",
        help="show entropy and strength (on stderr)",
    )

    sub = parser.add_subparsers(dest="command", required=True, metavar="COMMAND")

    # --- password -------------------------------------------------------
    pw = sub.add_parser(
        "password", parents=[common],
        help="password of random characters",
        description="Generate passwords of random characters.",
    )
    pw.add_argument("-l", "--length", type=int, default=16,
                    help="length (default 16)")
    pw.add_argument("-s", "--symbols", action="store_true",
                    help="include symbols (!@#$...)")
    pw.add_argument("--no-upper", action="store_true", help="no uppercase letters")
    pw.add_argument("--no-lower", action="store_true", help="no lowercase letters")
    pw.add_argument("--no-digits", action="store_true", help="no digits")
    pw.add_argument("--no-ambiguous", action="store_true",
                    help="exclude ambiguous characters (0 O 1 l I)")

    # --- passphrase -----------------------------------------------------
    pp = sub.add_parser(
        "passphrase", parents=[common],
        help="passphrase of random words",
        description="Generate passphrases from the EFF wordlist.",
    )
    pp.add_argument("-w", "--words", type=int, default=6,
                    help="number of words (default 6)")
    pp.add_argument("--separator", default="-",
                    help="separator between words (default '-')")
    pp.add_argument("--capitalize", action="store_true",
                    help="capitalize the first letter of each word")
    pp.add_argument("-n", "--number", action="store_true",
                    help="append a digit to a random word")

    return parser


def _run_password(args: argparse.Namespace) -> tuple[list[str], float]:
    opts = Options(
        length=args.length,
        upper=not args.no_upper,
        lower=not args.no_lower,
        digits=not args.no_digits,
        symbols=args.symbols,
        exclude_ambiguous=args.no_ambiguous,
    )
    results = [generate_password(opts) for _ in range(args.count)]
    return results, entropy_bits(opts.length, pool_size(opts))


def _run_passphrase(args: argparse.Namespace) -> tuple[list[str], float]:
    opts = PassphraseOptions(
        words=args.words,
        separator=args.separator,
        capitalize=args.capitalize,
        add_number=args.number,
    )
    results = [generate_passphrase(opts) for _ in range(args.count)]
    return results, passphrase_entropy_bits(opts)


def main(argv: list[str] | None = None) -> int:
    """Entry point. Returns the process exit code (0 = success).

    `argv` defaults to sys.argv[1:]; tests pass their own list instead.
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    runners = {"password": _run_password, "passphrase": _run_passphrase}
    try:
        results, bits = runners[args.command](args)
    except ValueError as e:
        # Invalid options from the core: show a clean message, not a traceback.
        # parser.error() prints usage + message to stderr and exits with code 2.
        parser.error(str(e))

    # Results go to stdout; extra information goes to stderr, so that
    # `python -m password_core password > file.txt` saves only passwords.
    for r in results:
        print(r)
    if args.entropy:
        print(f"{bits:.1f} bits · {strength_label(bits)}", file=sys.stderr)
    return 0
