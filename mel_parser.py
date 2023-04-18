from contextlib import suppress
import inspect

import pyparsing as pp
from pyparsing import pyparsing_common as ppc

from mel_ast import *


def _make_parser():
    num = ppc.fnumber
    ident = ppc.identifier

    LPAR, RPAR = pp.Literal('(').suppress(), pp.Literal(')').suppress()
    LBRACE, RBRACE = pp.Literal('{').suppress(), pp.Literal('}').suppress()
    ASSIGN = pp.Literal('=')
    MULT, ADD = pp.oneOf(('* /')), pp.oneOf(('+ -'))
    COMPARE = pp.oneOf('> >= < <= == != || &&')
    TYPE = pp.oneOf('int double string bool char float void')
    END = pp.Literal(';').suppress()
    DOT = pp.Literal('.').suppress()
    COMMA = pp.Literal(',').suppress()
    # типы данных
    # INT = pp.Keyword('int')
    # DOUBLE = pp.Keyword('double')
    # STRING = pp.Keyword('string')
    # BOOL = pp.Keyword('bool')
    # CHAR = pp.Keyword('char')
    # FLOAT = pp.Keyword('float')

    CON = pp.Keyword('Console')
    INPUT = pp.Keyword('ReadLine')
    OUTPUT = pp.Keyword('WriteLine')
    RETURN = pp.Keyword('return')

    ACCESS_MOD = pp.Keyword('private') | pp.Keyword('public') | pp.Keyword('protected')

    add = pp.Forward()

    paramDecl_ = TYPE + ident + pp.Optional(END)

    group = ident | num | LPAR + add + RPAR
    mult = group + pp.ZeroOrMore((COMPARE | MULT) + group)
    add << mult + pp.ZeroOrMore((COMPARE | ADD) + mult)

    expr = add

    stmt = pp.Forward()

    input = INPUT.suppress() + LPAR + ident + RPAR
    output = OUTPUT.suppress() + LPAR + add + RPAR
    console_ = CON.suppress() + DOT + (input | output) + END
    assign = (paramDecl_ | ident) + ASSIGN.suppress() + add + END
    return_ = RETURN.suppress() + add + END

    if_ = pp.Keyword("if").suppress() + LPAR + expr + RPAR + stmt + \
          pp.Optional(pp.Keyword("else").suppress() + stmt)
    while_ = pp.Keyword("while").suppress() + LPAR + expr + RPAR + stmt
    for_ = pp.Keyword("for").suppress() + LPAR + assign + add + END + add + RPAR + stmt

    method = ACCESS_MOD + TYPE + ident + \
             LPAR + pp.Optional(paramDecl_ + pp.ZeroOrMore(COMMA + paramDecl_)) + RPAR + \
             stmt
    class_ = pp.Keyword("class").suppress() + ident + LBRACE + pp.ZeroOrMore(method) + RBRACE

    stmt_list = pp.Forward()
    stmt << (assign | paramDecl_ | console_ | if_ | while_ | for_ | class_ | return_ | LBRACE + stmt_list + RBRACE)
    stmt_list << pp.ZeroOrMore(stmt)
    program = stmt_list.ignore(pp.cStyleComment).ignore(pp.dblSlashComment) + pp.StringEnd()

    start = program

    def set_parse_action_magic(rule_name: str, parser: pp.ParserElement) -> None:
        if rule_name == rule_name.upper():
            return
        if rule_name in ('mult', 'add'):
            def bin_op_parse_action(s, loc, tocs):
                node = tocs[0]
                for i in range(1, len(tocs) - 1, 2):
                    node = BinOpNode(BinOp(tocs[i]), node, tocs[i + 1])
                return node

            parser.setParseAction(bin_op_parse_action)
        if rule_name in 'paramDecl_':
            def type_parse_action(s, loc, tocs):
                node = ParamDeclNode(DeclType(tocs[0]), tocs[1])
                return node

            parser.setParseAction(type_parse_action)
        if rule_name in 'method':
            def method_parse_action(s, loc, tocs):
                params = tocs[3:-1]
                node = MethodNode(tocs[2], DeclType(tocs[1]), AccessMod(tocs[0]), params, tocs[-1])
                return node

            parser.setParseAction(method_parse_action)
        else:
            cls = ''.join(x.capitalize() for x in rule_name.split('_')) + 'Node'
            with suppress(NameError):
                cls = eval(cls)
                if not inspect.isabstract(cls):
                    def parse_action(s, loc, tocs):
                        return cls(*tocs)

                    parser.setParseAction(parse_action)

    for var_name, value in locals().copy().items():
        if isinstance(value, pp.ParserElement):
            set_parse_action_magic(var_name, value)

    return start


parser = _make_parser()


def parse(prog: str) -> StmtListNode:
    return parser.parseString(str(prog))[0]
