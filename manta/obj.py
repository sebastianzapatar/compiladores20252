
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

# ---------------- Object System ----------------

class Object:
    def type(self) -> str:
        raise NotImplementedError()

    def inspect(self) -> str:
        raise NotImplementedError()


# -- Primitive objects --
@dataclass
class Integer(Object):
    value: int

    def type(self) -> str:
        return "INTEGER"

    def inspect(self) -> str:
        return str(self.value)


@dataclass
class Boolean(Object):
    value: bool

    def type(self) -> str:
        return "BOOLEAN"

    def inspect(self) -> str:
        return "true" if self.value else "false"


class Null(Object):
    def type(self) -> str:
        return "NULL"

    def inspect(self) -> str:
        return "null"


# -- Function object --
@dataclass
class Function(Object):
    parameters: list   # List[Identifier] from AST, kept generic to avoid circular imports
    body: Any          # BlockStatement
    env: "Environment" # Captured environment (closure)

    def type(self) -> str:
        return "FUNCTION"

    def inspect(self) -> str:
        params = ", ".join(p.value for p in self.parameters)
        return f"fn({params}) {{ ... }}"


# -- Error object (non-fatal, flows through evaluator) --
@dataclass
class Error(Object):
    message: str

    def type(self) -> str:
        return "ERROR"

    def inspect(self) -> str:
        return f"ERROR: {self.message}"


# ---------------- Environment ----------------

class Environment:
    def __init__(self, outer: Optional["Environment"] = None) -> None:
        self.store: Dict[str, Object] = {}
        self.outer = outer

    def get(self, name: str) -> Optional[Object]:
        obj = self.store.get(name)
        if obj is None and self.outer is not None:
            return self.outer.get(name)
        return obj

    def set(self, name: str, value: Object) -> Object:
        self.store[name] = value
        return value


def new_enclosed_environment(outer: "Environment") -> "Environment":
    return Environment(outer=outer)


# Singletons
TRUE = Boolean(True)
FALSE = Boolean(False)
NULL = Null()
