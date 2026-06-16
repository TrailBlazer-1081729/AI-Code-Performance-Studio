import ast


class PrintRemover(ast.NodeTransformer):

    def visit_Expr(self, node):

        if (
            isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Name)
            and node.value.func.id == "print"
        ):
            return ast.Pass()

        return self.generic_visit(node)


def preprocess_code(code):

    tree = ast.parse(code)

    tree = PrintRemover().visit(tree)

    ast.fix_missing_locations(tree)

    return ast.unparse(tree)