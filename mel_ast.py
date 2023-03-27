from abc import ABC, abstractmethod
from typing import Callable, Tuple, Optional, Union
from enum import Enum


class AstNode(ABC):
    @property
    def childs(self) -> Tuple['AstNode', ...]:
        return ()

    @abstractmethod
    def __str__(self) -> str:
        pass

    @property
    def tree(self) -> [str, ...]:
        res = [str(self)]
        childs = self.childs
        for i, child in enumerate(childs):
            ch0, ch = '├', '│'
            if i == len(childs) - 1:
                ch0, ch = '└', ' '
            res.extend(((ch0 if j == 0 else ch) + ' ' + s for j, s in enumerate(child.tree)))
        return res

    def visit(self, func: Callable[['AstNode'], None]) -> None:
        func(self)
        map(func, self.childs)

    def __getitem__(self, index):
        return self.childs[index] if index < len(self.childs) else None


class ExprNode(AstNode):
    pass


class NumNode(ExprNode):
    def __init__(self, num: float):
        super().__init__()
        self.num = float(num)

    def __str__(self) -> str:
        return str(self.num)


class IdentNode(ExprNode):
    def __init__(self, name: str):
        super().__init__()
        self.name = str(name)

    def __str__(self) -> str:
        return str(self.name)


class DeclType(Enum):
    INT = 'int'
    DOUBLE = 'double'
    STRING = 'string'
    BOOL = 'bool'
    CHAR = 'char'
    FLOAT = 'float'
    VOID = 'void'


class ParamDeclNode(AstNode):
    def __init__(self, type_: DeclType, name: IdentNode):
        super().__init__()
        self.type_ = type_
        self.name = name

    @property
    def childs(self) -> tuple[IdentNode]:
        return self.name,

    def __str__(self) -> str:
        return str(self.type_.value)


class ParamDeclListNode(AstNode):
    def __init__(self, *params: AstNode):
        super().__init__()
        self.params = params

    @property
    def childs(self) -> Tuple[AstNode]:
        return self.params

    def __str__(self) -> str:
        return 'params'


class BinOp(Enum):
    ADD = '+'
    SUB = '-'
    MUL = '*'
    DIV = '/'
    GT = '>'
    GE = '>='
    LT = '<'
    LE = '<='
    EQ = '=='
    NE = '!='
    OR = '||'
    AND = '&&'


class BinOpNode(ExprNode):
    def __init__(self, op: BinOp, arg1: ExprNode, arg2: ExprNode):
        super().__init__()
        self.op = op
        self.arg1 = arg1
        self.arg2 = arg2

    @property
    def childs(self) -> Tuple[ExprNode, ExprNode]:
        return self.arg1, self.arg2

    def __str__(self) -> str:
        return str(self.op.value)


class InputNode(AstNode):
    def __init__(self, var: IdentNode):
        super().__init__()
        self.var = var

    @property
    def childs(self) -> tuple[IdentNode]:
        return self.var,

    def __str__(self) -> str:
        return 'ReadLine'


class ConsoleNode(AstNode):
    def __init__(self, method: AstNode):
        super().__init__()
        self.method = method

    @property
    def childs(self) -> tuple[AstNode]:
        return self.method,

    def __str__(self) -> str:
        return 'Console'


class OutputNode(AstNode):
    def __init__(self, arg: ExprNode):
        super().__init__()
        self.arg = arg

    @property
    def childs(self) -> tuple[ExprNode]:
        return self.arg,

    def __str__(self) -> str:
        return 'WriteLine'


class StmtNode(AstNode):
    pass


class AssignNode(StmtNode):
    def __init__(self, var: (ParamDeclNode | IdentNode), val: ExprNode):
        super().__init__()
        self.var = var
        self.val = val

    @property
    def childs(self) -> Tuple[(ParamDeclNode | IdentNode), ExprNode]:
        return self.var, self.val

    def __str__(self) -> str:
        return '='


class ReturnNode(AstNode):
    def __init__(self, arg: ExprNode):
        self.arg = arg

    @property
    def childs(self) -> Tuple[ExprNode]:
        return self.arg,

    def __str__(self) -> str:
        return 'return'


class IfNode(StmtNode):
    def __init__(self, cond: ExprNode, then_stmt: StmtNode, else_stmt: Optional[StmtNode] = None):
        super().__init__()
        self.cond = cond
        self.then_stmt = then_stmt
        self.else_stmt = else_stmt

    @property
    def childs(self) -> tuple[ExprNode | StmtNode, ...]:
        return (self.cond, self.then_stmt) + ((self.else_stmt,) if self.else_stmt else tuple())

    def __str__(self) -> str:
        return 'if'


class WhileNode(StmtNode):
    def __init__(self, cond: ExprNode, body: StmtNode):
        super().__init__()
        self.cond = cond
        self.body = body

    @property
    def childs(self) -> Tuple[ExprNode, StmtNode]:
        return self.cond, self.body

    def __str__(self) -> str:
        return 'while'


class ForNode(StmtNode):
    def __init__(self, init: AssignNode, cond: ExprNode, incr: ExprNode, body: StmtNode):
        super().__init__()
        self.init = init
        self.cond = cond
        self.incr = incr
        self.body = body

    @property
    def childs(self) -> tuple[AssignNode, ExprNode, ExprNode, StmtNode]:
        return self.init, self.cond, self.incr, self.body

    def __str__(self) -> str:
        return 'for'


class StmtListNode(AstNode):
    def __init__(self, *exprs: AstNode):
        super().__init__()
        self.exprs = exprs

    @property
    def childs(self) -> Tuple[AstNode]:
        return self.exprs

    def __str__(self) -> str:
        return '...'


class AccessMod(Enum):
    PUBLIC = 'public'
    PRIVATE = 'private'
    PROTECTED = 'protected'


class StaticMod(Enum):
    STATIC = 'static'


class MethodDeclNode(StmtNode):
    def __init__(self, access_mod: AccessMod, type_: DeclType):
        super().__init__()
        self.access_mod = access_mod
        self.type_ = type_

    def __str__(self) -> str:
        return str(self.access_mod.value) + ' ' + str(self.type_.value)


class MethodNode(StmtNode):
    def __init__(self, decl: MethodDeclNode, name: IdentNode, param: Optional[ParamDeclNode] = None,
                 stmt: Optional[StmtNode] = None):
        super().__init__()
        self.decl = decl
        self.name = name
        self.param = param
        self.stmt = stmt

    @property
    def childs(self) -> tuple[ParamDeclNode, ...] | tuple[ParamDeclNode | StmtNode, ...]:
        return ((self.param,) if self.param else tuple()) + ((self.stmt,) if self.stmt else tuple())

    def __str__(self) -> str:
        return self.decl.__str__() + ' ' + str(self.name)


class ClassNode(StmtNode):
    def __init__(self, name: IdentNode, stmt: Optional[StmtNode] = None):
        super().__init__()
        self.name = name
        self.stmt = stmt

    @property
    def childs(self) -> tuple[IdentNode, ...] | tuple[IdentNode | StmtNode, ...]:
        return (self.name,) + ((self.stmt,) if self.stmt else tuple())

    def __str__(self) -> str:
        return 'class'
