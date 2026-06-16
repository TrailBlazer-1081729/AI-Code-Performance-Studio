import ast
import copy
import statistics
import time
import tracemalloc

def get_functions(code):
    tree = ast.parse(code)
    functions = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            functions.append(
                {
                    "name": node.name,
                    "args": [
                        arg.arg
                        for arg in node.args.args
                    ]
                }
            )
        elif isinstance(node, ast.ClassDef):
            for item in node.body:
                if (
                    isinstance(item, ast.FunctionDef)
                    and not item.name.startswith("__")
                ):
                    functions.append(
                        {
                            "name": item.name,
                            "args": [
                                arg.arg
                                for arg in item.args.args
                                if arg.arg != "self"
                            ]
                        }
                    )

    return functions


class BenchmarkEngine:

    def __init__(
        self,
        code,
        generated_input,
        runs=5
    ):
        self.code = code
        self.generated_input = generated_input
        self.runs = runs

    def benchmark(
        self,
        function_name
    ):

        namespace = {}

        exec(
            self.code,
            namespace
        )


        if function_name in namespace:

            func = namespace[function_name]

        elif "Solution" in namespace:

            solution = namespace["Solution"]()

            func = getattr(
                solution,
                function_name
            )

        else:

            raise ValueError(
                f"Unable to locate function '{function_name}'"
            )

        warmup_input = copy.deepcopy(
            self.generated_input
        )

        if isinstance(
            warmup_input,
            tuple
        ):
            func(*warmup_input)
        else:
            func(warmup_input)

        timings = []

        peak_memory = 0

        for _ in range(
            self.runs
        ):

            current_input = (
                copy.deepcopy(
                    self.generated_input
                )
            )

            tracemalloc.start()
            start = (
                time.perf_counter()
            )
            if isinstance(
                current_input,
                tuple
            ):
                func(
                    *current_input
                )
            else:
                func(
                    current_input
                )
            end = (
                time.perf_counter()
            )

            current, peak = (
                tracemalloc
                .get_traced_memory()
            )

            tracemalloc.stop()

            timings.append(
                end - start
            )

            peak_memory = max(
                peak_memory,
                peak
            )

        return {

            "function_name":
                function_name,

            "runs":
                self.runs,

            "avg_time":
                sum(timings)
                / len(timings),

            "median_time":
                statistics.median(
                    timings
                ),

            "best_time":
                min(timings),

            "worst_time":
                max(timings),

            "total_time":
                sum(timings),

            "peak_memory_kb":
                peak_memory
                / 1024
        }