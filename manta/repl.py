from manta.tokens import TokenType
from manta.lexer import Lexer
from manta.parser import Parser
from manta.evaluator import evaluate
from manta.obj import Environment

PROMPT = ">> "

def start():
    
    env = Environment()
    while True:
        try:
            line = input(PROMPT)
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break

        if not line.strip():
            continue

        l = Lexer(line)
        p = Parser(l)
        program = p.parse_program()

        if len(p.errors) > 0:
            print("Parser errors:")
            for e in p.errors:
                print(f"  - {e}")
            continue

        result = evaluate(program, env)
        print(result.inspect())

if __name__ == "__main__":
    start()
