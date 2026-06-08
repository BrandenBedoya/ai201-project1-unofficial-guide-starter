"""Command-line interface for The Unofficial Guide.

    python ask.py "Which professor should I take for CS61A?"     # one-shot
    python ask.py                                                # interactive loop

Prints the grounded answer and the sources it drew from.
"""
import sys

from generate import answer


def _print_result(question: str) -> None:
    r = answer(question)
    print(f"\nQ: {question}\n")
    print(r["answer"])
    if r["sources"]:
        print("\nSources:")
        for s in r["sources"]:
            print(f"  • {s}")
    print(f"\n(top match distance: {r['top_distance']})")


def main() -> None:
    if len(sys.argv) > 1:
        _print_result(" ".join(sys.argv[1:]))
        return
    print("The Unofficial Guide — ask about UC Berkeley CS professors. (Ctrl-C to quit)")
    try:
        while True:
            q = input("\n> ").strip()
            if q:
                _print_result(q)
    except (KeyboardInterrupt, EOFError):
        print("\nbye!")


if __name__ == "__main__":
    main()
