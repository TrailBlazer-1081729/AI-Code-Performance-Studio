import ast

class CallGraphBuilder(ast.NodeVisitor):
    def __init__(self):
        self.current_function = None
        self.calls = {}
    def visit_FunctionDef(self, node):
        self.current_function = node.name
        self.calls.setdefault(
            node.name,
            set()
        )
        self.generic_visit(node)
        self.current_function = None
    def visit_Call(self, node):
        if (
            self.current_function
            and isinstance(
                node.func,
                ast.Name
            )
        ):
            self.calls[
                self.current_function
            ].add(
                node.func.id
            )
        self.generic_visit(node)




def find_entry_functions(graph):

    incoming = {
        func: 0
        for func in graph
    }

    for caller in graph:

        for callee in graph[caller]:

            if callee in incoming:

                incoming[callee] += 1

    return [
        func
        for func, count
        in incoming.items()
        if count == 0
    ]
def build_call_graph(code):
    tree = ast.parse(code)
    builder = (
        CallGraphBuilder()
    )
    builder.visit(tree)
    return find_entry_functions(builder.calls)[0]

