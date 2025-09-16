from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional
from manta.tokens import Token, TokenType

# ----------------- Base Nodes -----------------
class Node:
    def token_literal(self) -> str:
        raise NotImplementedError()

    def __str__(self) -> str:
        return self.string()

    def string(self) -> str:
        raise NotImplementedError()

class Statement(Node):
    pass

class Expression(Node):
    pass

# ----------------- Program -----------------
@dataclass
class Program(Node):
    statements: List[Statement]

    def token_literal(self) -> str:
        return self.statements[0].token_literal() if self.statements else ""

    def string(self) -> str:
        return "".join(s.string() for s in self.statements)

# ----------------- Statements -----------------
@dataclass
class LetStatement(Statement):
    token: Token          # TokenType.LET
    name: 'Identifier'
    value: Optional[Expression]

    def token_literal(self) -> str:
        return self.token.literal

    def string(self) -> str:
        out = f"{self.token_literal()} {self.name.string()}"
        if self.value is not None:
            out += f" = {self.value.string()}"
        out += ";"
        return out

@dataclass
class ExpressionStatement(Statement):
    token: Token
    expression: Optional[Expression]

    def token_literal(self) -> str:
        return self.token.literal

    def string(self) -> str:
        return "" if self.expression is None else self.expression.string()

@dataclass
class BlockStatement(Statement):
    token: Token  # the '{' token
    statements: List[Statement]

    def token_literal(self) -> str:
        return self.token.literal

    def string(self) -> str:
        return "".join(s.string() for s in self.statements)

# ----------------- Expressions -----------------
@dataclass
class Identifier(Expression):
    token: Token
    value: str

    def token_literal(self) -> str:
        return self.token.literal

    def string(self) -> str:
        return self.value

@dataclass
class IntegerLiteral(Expression):
    token: Token
    value: int

    def token_literal(self) -> str:
        return self.token.literal

    def string(self) -> str:
        return str(self.value)

@dataclass
class Boolean(Expression):
    token: Token
    value: bool

    def token_literal(self) -> str:
        return self.token.literal

    def string(self) -> str:
        return "true" if self.value else "false"

@dataclass
class PrefixExpression(Expression):
    token: Token    # operator token, e.g. ! or -
    operator: str
    right: Expression

    def token_literal(self) -> str:
        return self.token.literal

    def string(self) -> str:
        return f"({self.operator}{self.right.string()})"

@dataclass
class InfixExpression(Expression):
    token: Token    # operator token
    left: Expression
    operator: str
    right: Expression

    def token_literal(self) -> str:
        return self.token.literal

    def string(self) -> str:
        return f"({self.left.string()} {self.operator} {self.right.string()})"

@dataclass
class IfExpression(Expression):
    token: Token   # 'if'
    condition: Expression
    consequence: BlockStatement
    alternative: Optional[BlockStatement]

    def token_literal(self) -> str:
        return self.token.literal

    def string(self) -> str:
        out = f"if {self.condition.string()} {self.consequence.string()}"
        if self.alternative is not None:
            out += f" else {self.alternative.string()}"
        return out

@dataclass
class FunctionLiteral(Expression):
    token: Token  # 'function'
    parameters: List['Identifier']
    body: BlockStatement

    def token_literal(self) -> str:
        return self.token.literal

    def string(self) -> str:
        params = ", ".join(p.string() for p in self.parameters)
        return f"{self.token_literal()}({params}) {self.body.string()}"

@dataclass
class CallExpression(Expression):
    token: Token       # '('
    function: Expression   # Identifier or FunctionLiteral
    arguments: List[Expression]

    def token_literal(self) -> str:
        return self.token.literal

    def string(self) -> str:
        args = ", ".join(a.string() for a in self.arguments)
        return f"{self.function.string()}({args})"
