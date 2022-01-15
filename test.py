from typing import Sequence

import libcst
from libcst import (
    Arg,
    Attribute,
    Call,
    ClassDef,
    FunctionDef,
    List,
    Module,
    SimpleString,
)


def handle_decorator(func_name: str, call: Call) -> None:
    func: Attribute = call.func
    args: Sequence[Arg] = call.args
    decorator_obj_name: str = func.value.value
    decorator_obj_func: str = func.attr.value

    # found Flask decorator `@app.route`
    if decorator_obj_name == 'app' and decorator_obj_func == 'route':
        args_str: str = ''

        for arg in args:
            if arg.keyword is not None:
                args_str += f'{arg.keyword.value}='

            if isinstance(arg.value, SimpleString):
                args_str += f'{arg.value.value}'

            elif isinstance(arg.value, List):
                args_str += '[ '
                for element in arg.value.elements:
                    if isinstance(element.value, SimpleString):
                        args_str += f'{element.value.value}, '
                args_str += ' ]'

            args_str += ' '

        print(f'Found @{decorator_obj_name}.{decorator_obj_func} -> ', end='')
        print(f'on {func_name} {args_str.strip()}\n')


def parse_module(source_code: str) -> None:

    source_tree: Module = libcst.parse_module(source_code)

    for statement in source_tree.body:
        # for each function in this module
        if isinstance(statement, FunctionDef):
            func_name: str = statement.name.value

            # for each decorators in this function
            for decorator in statement.decorators:
                if isinstance(decorator.decorator, Call):
                    handle_decorator(func_name, decorator.decorator)
                elif isinstance(decorator.decorator, ClassDef):
                    # what to do?
                    pass
                else:
                    print(
                        'A decorator can be either a call to function or class'
                    )


test_code = """
from flask import Flask
app = Flask(__name__)

@app.route('/login', methods=['GET', 'POST'])
def login():
    pass

@app.route('/')
def hello():
    pass

@app.route('/<name>')
def hello_name(name):
    pass

if __name__ == '__main__':
    app.run()
"""

if __name__ == '__main__':
    parse_module(test_code)

    # output
    """
    Found @app.route -> on login '/login' methods=[ 'GET', 'POST',  ]

    Found @app.route -> on hello '/'

    Found @app.route -> on hello_name '/<name>'

    """
