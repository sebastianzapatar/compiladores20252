from re import match
from manta.tokens import (
    TokenType,
    Token,
    lookup_token_type,
)

class Lexer:
    def __init__(self, source: str) -> None:
        self.__source: str = source or ""
        self.__character: str = ""
        self.__read_position: int = 0  # índice del próximo char a leer
        self.__position: int = 0       # índice del char actual
        self.__read_character()

    # --- API pública ---------------------------------------------------------
    def next_token(self) -> Token:
        self.__skip_whitespace()

        ch = self.__character

        # Fin de la entrada
        if ch == "":
            return Token(TokenType.EOF, "")

        # Operadores de dos caracteres primero: ==, !=, >=
        if ch == "=" and self.__peek_character() == "=":
            literal = ch + self.__peek_character()
            self.__read_character()
            self.__read_character()
            return Token(TokenType.EQ, literal)

        if ch == "!" and self.__peek_character() == "=":
            literal = ch + self.__peek_character()
            self.__read_character()
            self.__read_character()
            return Token(TokenType.NOT_EQ, literal)

        if ch == ">" and self.__peek_character() == "=":
            literal = ch + self.__peek_character()
            self.__read_character()
            self.__read_character()
            return Token(TokenType.GTE, literal)

        # Tokens de un carácter
        single_map = {
            "=": TokenType.ASSIGN,
            "+": TokenType.PLUS,
            "-": TokenType.MINUS,
            "*": TokenType.MULTIPLICATION,
            "/": TokenType.DIVISSION,   # Nota: nombre tal cual en tu enum
            "!": TokenType.NEGATION,
            "<": TokenType.LT,
            ">": TokenType.GT,
            "(": TokenType.LPAREN,
            ")": TokenType.RPAREN,
            "{": TokenType.LBRACE,
            "}": TokenType.RBRASE,      # Nota: nombre tal cual en tu enum
            ",": TokenType.COMMA,
            ";": TokenType.SEMICOLON,
        }

        if ch in single_map:
            tok = Token(single_map[ch], ch)
            self.__read_character()
            return tok

        # Números
        if self.__is_digit(ch):
            literal = self.__read_number()
            return Token(TokenType.INT, literal)

        # Identificadores / keywords: [a-zA-Z_][a-zA-Z0-9_]*
        if self.__is_letter(ch) or ch == "_":
            literal = self.__read_identifier()
            tok_type = lookup_token_type(literal)
            return Token(tok_type, literal)

        # Cualquier otro símbolo es ILLEGAL
        illegal = Token(TokenType.ILLEGAL, ch)
        self.__read_character()
        return illegal

    # --- Helpers --------------------------------------------------------------
    def __read_character(self) -> None:
        """Avanza un carácter; pone '' en EOF."""
        if self.__read_position >= len(self.__source):
            self.__character = ""
        else:
            self.__character = self.__source[self.__read_position]
        self.__position = self.__read_position
        self.__read_position += 1

    def __peek_character(self) -> str:
        """Mira un carácter adelante sin consumirlo."""
        if self.__read_position >= len(self.__source):
            return ""
        return self.__source[self.__read_position]

    def __is_digit(self, character: str) -> bool:
        return bool(match(r'^\d$', character))

    def __read_number(self) -> str:
        start = self.__position
        while self.__is_digit(self.__character):
            self.__read_character()
        return self.__source[start:self.__position]

    def __skip_whitespace(self) -> None:
        while self.__character != "" and self.__character.isspace():
            self.__read_character()

    def __is_letter(self, character: str) -> bool:
        # Importante: validar el parámetro recibido, no self.__character
        return bool(match(r'^[a-zA-Z]$', character))

    def __read_identifier(self) -> str:
        start = self.__position
        # primer char debe ser letra o guion bajo
        if self.__is_letter(self.__character) or self.__character == "_":
            self.__read_character()
        # siguientes: letras, dígitos o guion bajo
        while (
            self.__is_letter(self.__character)
            or self.__is_digit(self.__character)
            or self.__character == "_"
        ):
            self.__read_character()
        return self.__source[start:self.__position]
