from re import match
from manta.tokens import (
    TokenType,
    Token
)
class Lexer:
    def __init__(self, source:str)->None:
        self.__source:str=source
        self.__character:str=''
        self.__read_position:int=0
        self.__position:int=0
        self.__read_character()
    def next_token(self)->TokenType:
        if match(r'^=$',self.__character):
            token=Token(TokenType.ASSIGN,self.__character)
        elif match(r'^\+$',self.__character):
            token=Token(TokenType.PLUS, self.__character)
        elif match(r'^\*$',self.__character):
            token=Token(TokenType.MULTIPLICATION,self.__character)
        elif self._is_number(self.__character):
            literal=self.__read_number()
            return Token(TokenType.INT,literal)   
        elif self.__character=='':
            token=Token(TokenType.EOF,'')
        else:
            token=Token(TokenType.ILLEGAL,self.__character)
        self.__read_character()
        return token
    def __read_character(self)->None:
        if self.__read_position>=len(self.__source):
            
            self.__character=''
        else:
            self.__character=self.__source[self.__read_position]
        self.__position=self.__read_position
        self.__read_position+=1
    def _is_number(self,character:str)->bool:
        return bool(match(r'^\d$',character))
    def __read_number(self)->str:
        initial_position=self.__position
        while self._is_number(self.__character):
            self.__read_character()
        return self.__source[initial_position:self.__position]
