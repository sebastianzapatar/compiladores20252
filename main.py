
#!/usr/bin/env python3
import sys


from manta.lexer import Lexer
from manta.parser import Parser
from manta.evaluator import evaluate
from manta.obj import Environment


def run_source(code: str) -> int:
    """Lex + parse + evaluate the whole source file. Returns process exit code."""
    lexer = Lexer(code)
    parser = Parser(lexer)
    program = parser.parse_program()

    # If the parser exposes errors, print them and exit nonâ€‘zero.
    errs = getattr(parser, "errors", [])
    if errs:
        for e in errs:
            print(f"Parser error: {e}")
        return 2

    env = Environment()
    result = evaluate(program, env)
    # Most interpreters don't print NULL at top-level; you can change this.
    try:
        out = result.inspect()
    except Exception:
        out = str(result)
    print(out)
    return 0

def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("Usage: python main.py prueba.manta")
        return 1
    path = argv[1]
    try:
        with open(path, "r", encoding="utf-8") as f:
            src = f.read()
    except OSError as ex:
        print(f"Could not read file '{path}': {ex}")
        return 1
    return run_source(src)

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
