
from __future__ import annotations
from typing import List, Optional

from manta.ast import (
    Program, Statement, Expression, LetStatement, ExpressionStatement, BlockStatement,
    Identifier, IntegerLiteral, Boolean as AstBoolean,
    PrefixExpression, InfixExpression, IfExpression, FunctionLiteral, CallExpression
)
from .obj import (
    Object, Integer, Boolean, Null, Error, Function, Environment,
    TRUE, FALSE, NULL, new_enclosed_environment
)

# ------------- Public API -------------

def evaluate(node, env: Environment) -> Object:
    if isinstance(node, Program):
        return _eval_program(node, env)

    # Statements
    if isinstance(node, LetStatement):
        val = evaluate(node.value, env) if node.value is not None else NULL
        if _is_error(val):
            return val
        env.set(node.name.value, val)
        return val

    if isinstance(node, ExpressionStatement):
        return evaluate(node.expression, env) if node.expression is not None else NULL

    if isinstance(node, BlockStatement):
        return _eval_block_statement(node, env)

    # Expressions
    if isinstance(node, IntegerLiteral):
        return Integer(node.value)

    if isinstance(node, AstBoolean):
        return TRUE if node.value else FALSE

    if isinstance(node, PrefixExpression):
        right = evaluate(node.right, env)
        if _is_error(right):
            return right
        return _eval_prefix_expression(node.operator, right)

    if isinstance(node, InfixExpression):
        left = evaluate(node.left, env)
        if _is_error(left):
            return left
        right = evaluate(node.right, env)
        if _is_error(right):
            return right
        return _eval_infix_expression(node.operator, left, right)

    if isinstance(node, IfExpression):
        return _eval_if_expression(node, env)

    if isinstance(node, Identifier):
        val = env.get(node.value)
        if val is None:
            return Error(f"identifier not found: {node.value}")
        return val

    if isinstance(node, FunctionLiteral):
        fn = Function(parameters=node.parameters, body=node.body, env=env)
        return fn

    if isinstance(node, CallExpression):
        function = evaluate(node.function, env)
        if _is_error(function):
            return function
        args = _eval_expressions(node.arguments, env)
        if len(args) == 1 and _is_error(args[0]):
            return args[0]
        return _apply_function(function, args)

    return NULL


# ------------- Helpers -------------

def _eval_program(program: Program, env: Environment) -> Object:
    result: Object = NULL
    for stmt in program.statements:
        result = evaluate(stmt, env)
        if isinstance(result, Error):
            return result
    return result


def _eval_block_statement(block: BlockStatement, env: Environment) -> Object:
    result: Object = NULL
    for stmt in block.statements:
        result = evaluate(stmt, env)
        if isinstance(result, Error):
            return result
    return result


def _eval_prefix_expression(operator: str, right: Object) -> Object:
    if operator == "!":
        return _eval_bang_operator_expression(right)
    if operator == "-":
        if isinstance(right, Integer):
            return Integer(-right.value)
        return Error(f"unknown operator: -{right.type()}")
    return Error(f"unknown operator: {operator}{right.type()}")


def _eval_bang_operator_expression(right: Object) -> Object:
    if right is TRUE:
        return FALSE
    if right is FALSE:
        return TRUE
    if right is NULL:
        return TRUE
    return FALSE


def _eval_infix_expression(operator: str, left: Object, right: Object) -> Object:
    # Integer arithmetic and comparisons
    if isinstance(left, Integer) and isinstance(right, Integer):
        if operator == "+":
            return Integer(left.value + right.value)
        if operator == "-":
            return Integer(left.value - right.value)
        if operator == "*":
            return Integer(left.value * right.value)
        if operator == "/":
            if right.value == 0:
                return Error("division by zero")
            return Integer(left.value // right.value)
        if operator == "<":
            return TRUE if left.value < right.value else FALSE
        if operator == ">":
            return TRUE if left.value > right.value else FALSE
        if operator == ">=":
            return TRUE if left.value >= right.value else FALSE
        if operator == "==":
            return TRUE if left.value == right.value else FALSE
        if operator == "!=":
            return TRUE if left.value != right.value else FALSE
        return Error(f"unknown operator: {left.type()} {operator} {right.type()}")

    # Boolean equality
    if isinstance(left, Boolean) and isinstance(right, Boolean):
        if operator == "==":
            return TRUE if left.value == right.value else FALSE
        if operator == "!=":
            return TRUE if left.value != right.value else FALSE

    # Equality with different types -> false (like Monkey book) or error; we use error.
    if operator in ("==", "!="):
        return Error(f"type mismatch: {left.type()} {operator} {right.type()}")

    return Error(f"type mismatch: {left.type()} {operator} {right.type()}")


def _eval_if_expression(iexpr: IfExpression, env: Environment) -> Object:
    condition = evaluate(iexpr.condition, env)
    if _is_error(condition):
        return condition
    if _is_truthy(condition):
        return evaluate(iexpr.consequence, env)
    elif iexpr.alternative is not None:
        return evaluate(iexpr.alternative, env)
    else:
        return NULL


def _is_truthy(obj: Object) -> bool:
    if obj is NULL:
        return False
    if obj is TRUE:
        return True
    if obj is FALSE:
        return False
    if isinstance(obj, Integer):
        return obj.value != 0
    return True


def _eval_expressions(exps: List[Expression], env: Environment) -> List[Object]:
    result: List[Object] = []
    for e in exps:
        evaluated = evaluate(e, env)
        if _is_error(evaluated):
            return [evaluated]
        result.append(evaluated)
    return result


def _apply_function(fn_obj: Object, args: List[Object]) -> Object:
    if not isinstance(fn_obj, Function):
        return Error(f"not a function: {fn_obj.type()}")

    extended_env = new_enclosed_environment(fn_obj.env)
    # Bind parameters
    for i, param in enumerate(fn_obj.parameters):
        if i >= len(args):
            return Error(f"missing argument for parameter '{param.value}'")
        extended_env.set(param.value, args[i])

    # Evaluate body. No explicit return statements supported yet; last value wins.
    evaluated = evaluate(fn_obj.body, extended_env)
    return evaluated


def _is_error(obj: Object) -> bool:
    return isinstance(obj, Error)
