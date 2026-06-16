from Benchmark.Benchmark_controller import BenchmarkController
from ast_file import analyze_complexity
from TLE_ import TLEPredictor
import re
def normalize_complexity(c):
    c = c.strip()

    replacements = {
        "O(n^2)": "O(n²)",
        "O(n^3)": "O(n³)",
    }

    return replacements.get(c, c)

COMPLEXITY_RANK = {
    "O(1)": 1,
    "O(log n)": 2,
    "O(sqrt(n))": 3,
    "O(n)": 4,
    "O(n log n)": 5,
    "O(n sqrt(n))": 6,
    "O(n²)": 7,
    "O(n² log n)": 8,
    "O(n³)": 9,
    "O(2^n)": 10
}


def extract_complexity(text):
    matches = re.findall(
        r'O\([^)]+\)',
        text,
        flags=re.IGNORECASE
    )

    if matches:
        return matches[0]

    return "UNKNOWN"


class TLEController:

    def __init__(
        self,
        code,
        constraint,
        ast_result=None,
        benchmark_result=None
    ):
        self.code = code
        self.constraint = constraint
        self.ast_result = ast_result
        self.benchmark_result = benchmark_result

    def get_ast_complexity(self):

        if self.ast_result is not None:
            return self.ast_result

        summary, analysis = analyze_complexity(
            self.code
        )

        return extract_complexity(
            analysis
        )

    def get_benchmark_result(self):

        if self.benchmark_result is not None:
            return self.benchmark_result

        controller = BenchmarkController(
            code=self.code,
            max_n=5000
        )

        return controller.run()

    def choose_complexity(
        self,
        ast_complexity,
        benchmark_complexity
    ):
        ast_complexity = normalize_complexity(
            ast_complexity
        )

        benchmark_complexity = normalize_complexity(
            benchmark_complexity
        )

        if ast_complexity == benchmark_complexity:
            return ast_complexity, "HIGH"

        ast_rank = COMPLEXITY_RANK.get(
            ast_complexity,
            0
        )

        bench_rank = COMPLEXITY_RANK.get(
            benchmark_complexity,
            0
        )


        chosen = (
            ast_complexity
            if ast_rank > bench_rank
            else benchmark_complexity
        )

        return chosen, "MEDIUM"

    def parse_constraint(self):

        if (
                self.constraint is None
                or str(self.constraint).strip() == ""
        ):
            return 5000

        match = re.search(
            r"\d+",
            str(self.constraint)
        )

        if not match:
            return 5000

        return int(match.group())

    def run(self):

        ast_complexity = (
            self.get_ast_complexity()
        )

        benchmark_result = (
            self.get_benchmark_result()
        )

        benchmark_complexity = (
            benchmark_result["complexity"]
        )

        final_complexity, confidence = (
            self.choose_complexity(
                ast_complexity,
                benchmark_complexity
            )
        )
        print("AST:", ast_complexity)
        print("BENCH:", benchmark_complexity)
        print("FINAL:", final_complexity)

        target_n = (
            self.parse_constraint()
        )

        last_sample = (
            benchmark_result["benchmarks"][-1]
        )

        predictor = TLEPredictor(
            time_limit=1.0
        )

        prediction = predictor.predict(
            measured_time=last_sample[
                "avg_time"
            ],
            measured_n=last_sample[
                "size"
            ],
            target_n=target_n,
            complexity=final_complexity
        )

        return {
            "ast_complexity": ast_complexity,

            "benchmark_complexity": benchmark_complexity,

            "chosen_complexity": final_complexity,

            "confidence": confidence,

            "prediction": prediction,

            "benchmark_result": benchmark_result
        }