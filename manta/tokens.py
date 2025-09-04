from enum import (
    auto,
    Enum,
    unique
)
from typing import (
    NamedTuple,
    Dict
)
@unique
class TokenType(Enum):
    ASSIGN= auto()
    COMMA = auto()
    DIVISSION= auto()
    ELSE= auto()
    EOF= auto()
    EQ= auto()
    FALSE= auto()
    FUNCTION= auto()
    GT= auto()
    GTE= auto()
    IDENT= auto()
    IF= auto()
    ILLEGAL= auto()
    INT= auto()
    LBRACE= auto()
    LET= auto()
    LPAREN= auto()
    LT= auto()
    MINUS= auto()
    MULTIPLICATION= auto()
    NEGATION= auto()
    NOT_EQ=auto()
    PLUS=auto()
    RBRASE=auto()
    RETURN= auto()
    RPAREN= auto()
    SEMICOLON= auto()
    TRUE= auto()

class Token(NamedTuple):
    tokenType:TokenType
    literal:str#+ - if 
    def __str__(self):
        return f"Type: {self.tokenType}, Literal {self.literal}"


