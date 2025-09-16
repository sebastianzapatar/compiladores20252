from __future__ import annotations
from typing import Callable, Dict, List, Optional
from manta.tokens import TokenType, Token
from manta.lexer import Lexer
from manta.ast import (
    Program, Statement, Expression, LetStatement, ExpressionStatement, BlockStatement,
    Identifier, IntegerLiteral, Boolean, PrefixExpression, InfixExpression,
    IfExpression, FunctionLiteral, CallExpression
)

# Precedences (greater binds tighter)
LOWEST = 1
EQUALS = 2       # ==, !=
LESSGREATER = 3  # <, >, >=
SUM = 4          # + -
PRODUCT = 5      # * /
PREFIX = 6       # -X !X
CALL = 7         # myFunction(X)

PRECEDENCES = {
    TokenType.EQ: EQUALS,
    TokenType.NOT_EQ: EQUALS,
    TokenType.LT: LESSGREATER,
    TokenType.GT: LESSGREATER,
    TokenType.GTE: LESSGREATER,
    TokenType.PLUS: SUM,
    TokenType.MINUS: SUM,
    TokenType.MULTIPLICATION: PRODUCT,
    TokenType.DIVISSION: PRODUCT,
    TokenType.LPAREN: CALL,
}

PrefixParseFn = Callable[[], Optional[Expression]]
InfixParseFn = Callable[[Expression], Optional[Expression]]

class Parser:
    def __init__(self, lexer: Lexer) -> None:
        self.lexer = lexer
        self.errors: List[str] = []

        self.current_token: Token = Token(TokenType.ILLEGAL, "")
        self.peek_token: Token = Token(TokenType.ILLEGAL, "")

        # register parse functions
        self.prefix_fns: Dict[TokenType, PrefixParseFn] = {}
        self.infix_fns: Dict[TokenType, InfixParseFn] = {}

        self._register_prefix(TokenType.IDENT, self._parse_identifier)
        self._register_prefix(TokenType.INT, self._parse_integer_literal)
        self._register_prefix(TokenType.NEGATION, self._parse_prefix_expression)
        self._register_prefix(TokenType.MINUS, self._parse_prefix_expression)
        self._register_prefix(TokenType.TRUE, self._parse_boolean)
        self._register_prefix(TokenType.FALSE, self._parse_boolean)
        self._register_prefix(TokenType.LPAREN, self._parse_grouped_expression)
        self._register_prefix(TokenType.IF, self._parse_if_expression)
        self._register_prefix(TokenType.FUNCTION, self._parse_function_literal)

        self._register_infix(TokenType.PLUS, self._parse_infix_expression)
        self._register_infix(TokenType.MINUS, self._parse_infix_expression)
        self._register_infix(TokenType.MULTIPLICATION, self._parse_infix_expression)
        self._register_infix(TokenType.DIVISSION, self._parse_infix_expression)
        self._register_infix(TokenType.EQ, self._parse_infix_expression)
        self._register_infix(TokenType.NOT_EQ, self._parse_infix_expression)
        self._register_infix(TokenType.LT, self._parse_infix_expression)
        self._register_infix(TokenType.GT, self._parse_infix_expression)
        self._register_infix(TokenType.GTE, self._parse_infix_expression)
        self._register_infix(TokenType.LPAREN, self._parse_call_expression)

        # Initialize tokens
        self._advance_tokens()
        self._advance_tokens()

    # ------------- Public API -------------
    def parse_program(self) -> Program:
        statements: List[Statement] = []
        while self.current_token.tokenType != TokenType.EOF:
            stmt = self._parse_statement()
            if stmt is not None:
                statements.append(stmt)
            self._advance_tokens()
        return Program(statements=statements)

    # ------------- Helpers -------------
    def _advance_tokens(self) -> None:
        self.current_token = self.peek_token
        self.peek_token = self.lexer.next_token()

    def _expect_peek(self, t: TokenType) -> bool:
        if self.peek_token.tokenType == t:
            self._advance_tokens()
            return True
        self._peek_error(t)
        return False

    def _current_precedence(self) -> int:
        return PRECEDENCES.get(self.current_token.tokenType, LOWEST)

    def _peek_precedence(self) -> int:
        return PRECEDENCES.get(self.peek_token.tokenType, LOWEST)

    def _peek_error(self, t: TokenType) -> None:
        msg = f"expected next token to be {t}, got {self.peek_token.tokenType} instead"
        self.errors.append(msg)

    def _register_prefix(self, token_type: TokenType, fn: PrefixParseFn) -> None:
        self.prefix_fns[token_type] = fn

    def _register_infix(self, token_type: TokenType, fn: InfixParseFn) -> None:
        self.infix_fns[token_type] = fn

    # ------------- Statement Parsing -------------
    def _parse_statement(self) -> Optional[Statement]:
        if self.current_token.tokenType == TokenType.LET:
            return self._parse_let_statement()
        return self._parse_expression_statement()

    def _parse_let_statement(self) -> Optional[LetStatement]:
        tok = self.current_token

        if not self._expect_peek(TokenType.IDENT):
            return None
        name = Identifier(token=self.current_token, value=self.current_token.literal)

        if not self._expect_peek(TokenType.ASSIGN):
            return None

        self._advance_tokens()  # move to start of the expression
        value = self._parse_expression(LOWEST)

        if self.peek_token.tokenType == TokenType.SEMICOLON:
            self._advance_tokens()

        return LetStatement(token=tok, name=name, value=value)

    def _parse_expression_statement(self) -> ExpressionStatement:
        tok = self.current_token
        expr = self._parse_expression(LOWEST)

        if self.peek_token.tokenType == TokenType.SEMICOLON:
            self._advance_tokens()

        return ExpressionStatement(token=tok, expression=expr)

    # ------------- Expression Parsing -------------
    def _parse_expression(self, precedence: int) -> Optional[Expression]:
        prefix = self.prefix_fns.get(self.current_token.tokenType)
        if prefix is None:
            self.errors.append(f"no prefix parse function for {self.current_token.tokenType}")
            return None
        left_exp = prefix()

        while (
            self.peek_token.tokenType != TokenType.SEMICOLON
            and precedence < self._peek_precedence()
        ):
            infix = self.infix_fns.get(self.peek_token.tokenType)
            if infix is None:
                return left_exp
            self._advance_tokens()
            left_exp = infix(left_exp)  # type: ignore
        return left_exp

    # ---- Prefix parse fns ----
    def _parse_identifier(self) -> Identifier:
        return Identifier(token=self.current_token, value=self.current_token.literal)

    def _parse_integer_literal(self) -> Optional[IntegerLiteral]:
        try:
            value = int(self.current_token.literal)
        except ValueError:
            self.errors.append(f"could not parse integer: {self.current_token.literal}")
            return None
        return IntegerLiteral(token=self.current_token, value=value)

    def _parse_boolean(self) -> Boolean:
        return Boolean(token=self.current_token, value=self.current_token.tokenType == TokenType.TRUE)

    def _parse_prefix_expression(self) -> Optional[PrefixExpression]:
        tok = self.current_token
        operator = self.current_token.literal
        self._advance_tokens()
        right = self._parse_expression(PREFIX)
        if right is None:
            return None
        return PrefixExpression(token=tok, operator=operator, right=right)

    def _parse_grouped_expression(self) -> Optional[Expression]:
        self._advance_tokens()
        exp = self._parse_expression(LOWEST)
        if not self._expect_peek(TokenType.RPAREN):
            return None
        return exp

    def _parse_if_expression(self) -> Optional[IfExpression]:
        tok = self.current_token
        if not self._expect_peek(TokenType.LPAREN):
            return None
        self._advance_tokens()
        condition = self._parse_expression(LOWEST)
        if condition is None:
            return None
        if not self._expect_peek(TokenType.RPAREN):
            return None
        if not self._expect_peek(TokenType.LBRACE):
            return None
        consequence = self._parse_block_statement()

        alternative = None
        if self.peek_token.tokenType == TokenType.ELSE:
            self._advance_tokens()
            if not self._expect_peek(TokenType.LBRACE):
                return None
            alternative = self._parse_block_statement()

        return IfExpression(token=tok, condition=condition, consequence=consequence, alternative=alternative)

    def _parse_function_literal(self) -> Optional[FunctionLiteral]:
        tok = self.current_token
        if not self._expect_peek(TokenType.LPAREN):
            return None
        params = self._parse_function_parameters()
        if not self._expect_peek(TokenType.LBRACE):
            return None
        body = self._parse_block_statement()
        return FunctionLiteral(token=tok, parameters=params, body=body)

    def _parse_function_parameters(self) -> List[Identifier]:
        identifiers: List[Identifier] = []
        if self.peek_token.tokenType == TokenType.RPAREN:
            self._advance_tokens()
            return identifiers

        self._advance_tokens()
        ident = Identifier(token=self.current_token, value=self.current_token.literal)
        identifiers.append(ident)

        while self.peek_token.tokenType == TokenType.COMMA:
            self._advance_tokens()  # consume comma
            self._advance_tokens()  # move to next identifier
            ident = Identifier(token=self.current_token, value=self.current_token.literal)
            identifiers.append(ident)

        if not self._expect_peek(TokenType.RPAREN):
            return []
        return identifiers

    def _parse_block_statement(self) -> BlockStatement:
        tok = self.current_token
        self._advance_tokens()

        statements: List[Statement] = []
        while (
            self.current_token.tokenType != TokenType.RBRASE
            and self.current_token.tokenType != TokenType.EOF
        ):
            stmt = self._parse_statement()
            if stmt is not None:
                statements.append(stmt)
            self._advance_tokens()

        return BlockStatement(token=tok, statements=statements)

    # ---- Infix parse fns ----
    def _parse_infix_expression(self, left: Expression) -> Optional[InfixExpression]:
        tok = self.current_token
        operator = self.current_token.literal
        precedence = self._current_precedence()
        self._advance_tokens()
        right = self._parse_expression(precedence)
        if right is None:
            return None
        return InfixExpression(token=tok, left=left, operator=operator, right=right)

    def _parse_call_expression(self, function: Expression) -> CallExpression:
        return CallExpression(token=self.current_token, function=function, arguments=self._parse_call_arguments())

    def _parse_call_arguments(self) -> List[Expression]:
        args: List[Expression] = []
        if self.peek_token.tokenType == TokenType.RPAREN:
            self._advance_tokens()
            return args

        self._advance_tokens()
        arg = self._parse_expression(LOWEST)
        if arg is not None:
            args.append(arg)

        while self.peek_token.tokenType == TokenType.COMMA:
            self._advance_tokens()  # consume comma
            self._advance_tokens()  # move to next expression
            arg = self._parse_expression(LOWEST)
            if arg is not None:
                args.append(arg)

        if not self._expect_peek(TokenType.RPAREN):
            return []
        return args
