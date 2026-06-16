import ast
import json
import os
from dotenv import load_dotenv
import gradio as gr
import sqlite3
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("groq_api"))


def load_patterns():
    try:
        with open("patterns.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return [
            {"name": "Breadth-First Search (BFS)", "required_features": ["deque", "popleft"], "time": "O(V + E)",
             "space": "O(V)"},
            {"name": "Priority Queue / Dijkstra Baseline", "required_features": ["heap"], "time": "O(E log V)",
             "space": "O(V)"},
            {"name": "Sorting Pipeline", "required_features": ["sort"], "time": "O(n log n)", "space": "O(n)"},
            {"name": "Hash Table / Frequency Map", "required_features": ["dict"], "time": "O(n)", "space": "O(n)"},
            {"name": "Set Tracking / Deduplication", "required_features": ["set"], "time": "O(n)", "space": "O(n)"},
            {"name": "Binary Search", "required_features": ["binary_search_mid"], "time": "O(log n)", "space": "O(1)"},
            {"name": "Memoization", "required_features": ["dict", "memo_lookup"], "time": "O(n)", "space": "O(n)"}
        ]


patterns = load_patterns()


class CodeAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.functions = 0
        self.loops = 0
        self.imports = 0
        self.recursive_functions = set()
        self.current_function = None
        self.loop_depth = 0
        self.max_loop_depth = 0
        self.features = set()

    def visit_FunctionDef(self, node):
        self.functions += 1
        previous_function = self.current_function
        self.current_function = node.name
        self.generic_visit(node)
        self.current_function = previous_function

    def _handle_loop(self, node):
        self.loops += 1
        self.loop_depth += 1
        self.max_loop_depth = max(self.max_loop_depth, self.loop_depth)
        self.generic_visit(node)
        self.loop_depth -= 1

    def visit_For(self, node):
        self._handle_loop(node)

    def visit_While(self, node):
        self._handle_loop(node)

    def visit_Import(self, node):
        self.imports += 1
        for alias in node.names:
            if alias.name == "heapq":
                self.features.add("heap")
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        self.imports += 1
        if node.module == "collections":
            for alias in node.names:
                if alias.name == "deque":
                    self.features.add("deque")
        self.generic_visit(node)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Attribute):
            if node.func.attr == "popleft":
                self.features.add("popleft")
            elif node.func.attr == "sort":
                self.features.add("sort")

            if self.current_function and node.func.attr == self.current_function:
                self.recursive_functions.add(self.current_function)
                self.features.add("recursion")

        elif isinstance(node.func, ast.Name):
            if node.func.id == "dict":
                self.features.add("dict")
            elif node.func.id == "set":
                self.features.add("set")
            elif node.func.id == "sorted":
                self.features.add("sort")

            if self.current_function and node.func.id == self.current_function:
                self.recursive_functions.add(self.current_function)
                self.features.add("recursion")
        self.generic_visit(node)

    def visit_Dict(self, node):
        self.features.add("dict")
        self.generic_visit(node)

    def visit_DictComp(self, node):
        self.features.add("dict")
        self.generic_visit(node)

    def visit_Set(self, node):
        self.features.add("set")
        self.generic_visit(node)

    def visit_SetComp(self, node):
        self.features.add("set")
        self.generic_visit(node)

    def visit_Subscript(self, node):
        if isinstance(node.slice, ast.Slice):
            self.features.add("slicing")
        self.generic_visit(node)

    def visit_ListComp(self, node):
        self.features.add("list_comprehension")
        self.generic_visit(node)

    def visit_GeneratorExp(self, node):
        self.features.add("generator")
        self.generic_visit(node)

    def visit_Assign(self, node):
        if (
                len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)
                and node.targets[0].id == "mid"
        ):
            if (
                    isinstance(node.value, ast.BinOp)
                    and isinstance(node.value.op, ast.FloorDiv)
            ):
                self.features.add("binary_search_mid")
        self.generic_visit(node)

    def visit_Compare(self, node):
        if (
                len(node.ops) == 1
                and isinstance(node.ops[0], ast.In)
        ):
            if (
                    len(node.comparators) == 1
                    and isinstance(node.comparators[0], ast.Name)
                    and node.comparators[0].id in ["memo", "dp", "cache"]
            ):
                self.features.add("memo_lookup")
        self.generic_visit(node)


def analyze_code(code):
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return {
            "functions": 0,
            "loops": 0,
            "imports": 0,
            "recursive_functions": [],
            "max_loop_depth": 0,
            "has_nested_loops": False,
            "features": [],
            "possible_patterns": []
        }
    analyzer = CodeAnalyzer()
    analyzer.visit(tree)

    detected_features = list(analyzer.features)
    possible_patterns = []
    for pattern in patterns:
        reqs = pattern.get("required_features", pattern.get("keywords", []))
        if reqs and all(feature in detected_features for feature in reqs):
            possible_patterns.append({
                "name": pattern["name"],
                "time": pattern.get("time", "N/A"),
                "space": pattern.get("space", "N/A")
            })

    return {
        "functions": analyzer.functions,
        "loops": analyzer.loops,
        "imports": analyzer.imports,
        "recursive_functions": list(analyzer.recursive_functions),
        "max_loop_depth": analyzer.max_loop_depth,
        "has_nested_loops": analyzer.max_loop_depth > 1,
        "features": detected_features,
        "possible_patterns": possible_patterns
    }


def build_prompt(code, summary, pattern_list):
    formatted_features = "\n".join([f"- {feat}" for feat in summary.get("features", [])]) or "- None"
    pattern_notes = ""
    if summary.get("possible_patterns"):
        pattern_notes = "\nPossible Architectural Patterns Detected:\n"
        for p in summary["possible_patterns"]:
            pattern_notes += f"- {p['name']} (Expected Time: {p['time']}, Space: {p['space']})\n"

    prompt = f"""
    When analyzing complexity:
    1. Consider recursion depth.
    2. Consider list slicing costs.
    3. Consider list concatenation costs.
    4. Consider copying costs.
    5. Consider built-in operation complexities.
    6. Complexity should include output generation costs.
    7. Do not assume list append and list concatenation have the same complexity.

    AST Summary:
    Functions: {summary['functions']}
    Loops: {summary['loops']}
    Imports: {summary['imports']}
    Recursive Functions: {summary['recursive_functions']}
    Max Loop Nesting Depth: {summary.get('max_loop_depth', 0)}
    Has Nested Loops: {summary.get('has_nested_loops', False)}

    Detected AST Core Features:
    {formatted_features}
    {pattern_notes}
    Instructions:
    1. Analyze EACH function separately.
    2. If a function is recursive, analyze its recursion complexity even if it is never called.
    3. Analyze top-level executable code separately.
    4. Cross-verify the structural AST features against the code text to assert complexity.
    5. Report:
       - Time Complexity
       - Space Complexity
       - Reasoning
       - Optimizations
    Detected Features:
- recursion
- slicing
- binary_search_mid

IMPORTANT:
Pattern detections are structural hints only.
Do not derive complexity directly from detected patterns.
Derive complexity from the implementation.

    Code:
    {code}
    """
    return prompt


def analyze_complexity(code):
    summary = analyze_code(code)
    prompt = build_prompt(code, summary, patterns)
    messages = [
        {"role": "system", "content": sys_pr},
        {"role": "user", "content": prompt}
    ]
    print("CALLING COMPLEXITY ANALYZER")
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages
    )
    return summary, response.choices[0].message.content


sys_pr = """You are an expert code complexity analysis engine.

Your primary objective is correctness.

For every code sample:

Step 1: Identify all functions.

Step 2: Identify:

* loops
* nested loops
* recursion
* list slicing
* list concatenation
* sorting operations
* hashing operations
* copying operations
* heap operations
* queue operations
* set operations
* dictionary operations

Step 3: Estimate the cost of each significant operation.

Step 4: If recursion exists:

* Derive an explicit recurrence relation.
* Solve the recurrence before reporting complexity.
* Do not assume the complexity of a known algorithm.
* Analyze the actual implementation.

Examples:

T(n) = T(n/2) + O(1)
=> O(log n)

T(n) = T(n/2) + O(n)
=> O(n)

T(n) = 2T(n/2) + O(n)
=> O(n log n)

T(n) = 2T(n/2) + O(1)
=> O(n)

Step 5: Combine all costs to obtain:

* Time Complexity
* Space Complexity

Rules:

* Never assume binary-search-like code is O(log n).
* Never assume recursion is efficient.
* Never ignore slicing or copying costs.
* Never ignore allocation costs.
* Never ignore output generation costs.
* Never assume detected patterns determine final complexity.
* Pattern detection is only a hint, not proof.
Special Python List Operations:

list.pop(0) -> O(n)
list.insert(0,x) -> O(n)
list slicing -> O(n)
list.copy() -> O(n)
list.sort() -> O(n log n)
If such operations occur inside loops,
multiply their cost by the number of loop iterations.
When uncertainty exists:
* Explain competing interpretations.
* State assumptions.
* Assign a confidence level.
Output format:
Time Complexity:
...

Space Complexity:
...

Reasoning:
...

Optimizations:
...

Confidence:
...

"""

if __name__ == "__main__":
    print(analyze_complexity(""""""))