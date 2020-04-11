#!/usr/bin/env python
INTEGER, PLUS, MINUS, MUL, DIV, EOF = (
    'INTEGER', 'PLUS', 'MINUS', 'MUL', 'DIV', 'EOF'
)


class Token(object):
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self):
        return 'Token({type}, {value})'.format(
            type=self.type,
            value=repr(self.value)
        )

    def __repr__(self):
        return self.__str__()


class Lexer(object):
    def __init__(self, text):
        # client string input, e.g. "4 + 2 * 3 - 6 / 2"
        self.text = text
        self.pos = 0
        self.pre_flag = 1 #1 for operand before, 2 for num before
        self.flag = 0 #0 for no minus, 1 for minus 
        self.current_char = self.text[self.pos]

    def advance(self):
        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None  # Indicates end of input
        else:
            self.current_char = self.text[self.pos]

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def get_integer(self,flag):
        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        if self.flag==1:
        	self.flag = 0
        	self.pre_flag = 2
        	return -int(result)
        if self.flag == 0:
        	self.pre_flag = 2
        	return int(result)


    def get_next_token(self):
        while self.current_char is not None:

            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char.isdigit():

                return Token(INTEGER, self.get_integer(self.flag))

            if self.current_char == '+':
                self.advance()
                self.pre_flag = 1
                return Token(PLUS, '+')

            if self.current_char == '-':
                self.advance()
                if self.pre_flag == 1:
                	self.flag = 1
                	continue
                if self.pre_flag == 2:
                	self.flag = 1
                	return Token(PlUS, '+')

            if self.current_char == '*':
                self.advance()
                self.pre_flag = 1
                return Token(MUL, '*')

            if self.current_char == '/':
                self.advance()
                self.pre_flag = 1
                return Token(DIV, '/')

            self.error()

        return Token(EOF, None)


###############################################################################
#                                                                             #
#  PARSER                                                                     #
#                                                                             #
###############################################################################

class AST(object):
    pass


class BinaryOp(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right


class Num(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value


class Parser(object):
    def __init__(self, lexer):
        self.lexer = lexer
        flag = 0
        # set current token to the first token taken from the input
        self.current_token = self.lexer.get_next_token()

    def error(self):
        raise Exception('Invalid syntax')

    def eat(self, token_type):
        # compare the current token type with the passed token
        # type and if they match then "eat" the current token
        # and assign the next token to the self.current_token,
        # otherwise raise an exception.
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()

    def factor(self):
        """factor : INTEGER | LPAREN expr RPAREN"""
        token = self.current_token
        if token.type == INTEGER:
            self.eat(INTEGER)
            return Num(token)

    def term(self):
        """term : factor ((MUL | DIV) factor)*"""
        node = self.factor()

        while self.current_token.type in (MUL, DIV):
            token = self.current_token
            if token.type == MUL:
                self.eat(MUL)
            elif token.type == DIV:
                self.eat(DIV)

            node = BinaryOp(left=node, op=token, right=self.factor())

        return node

    def expr(self):
        node = self.term()

        while self.current_token.type in (PLUS, MINUS):
            token = self.current_token
            if token.type == PLUS:
                self.eat(PLUS)
            elif token.type == MINUS:
                self.eat(MINUS)

            node = BinaryOp(left=node, op=token, right=self.term())

        return node

    def parse(self):
        return self.expr()




class NodeVisitor(object):
    def traverse(self, node):
        method_name = 'traverse_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception('No visit_{} method'.format(type(node).__name__))


class Interpreter(NodeVisitor):
    def __init__(self, parser):
        self.parser = parser

    def traverse_BinaryOp(self, node):
        if node.op.type == PLUS:
            return self.traverse(node.left) + self.traverse(node.right)
        elif node.op.type == MUL:
            return self.traverse(node.left) * self.traverse(node.right)
        elif node.op.type == DIV:
            return self.traverse(node.left) / self.traverse(node.right)

    def traverse_Num(self, node):
        return node.value

    def interpret(self):
        tree = self.parser.parse()
        return self.traverse(tree)


def main():
    while True:
        try:
            try:
                text = raw_input('input: ')
            except NameError:  # Python3
                text = input('input: ')
        except EOFError:
            break
        if not text: 
            continue

        lexer = Lexer(text)
        parser = Parser(lexer)
        interpreter = Interpreter(parser)
        result = interpreter.interpret()
        print(result)


if __name__ == '__main__':
    main()
