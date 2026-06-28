import os
from dotenv import load_dotenv
from Benchmark.complexity import ComplexityEstimator

from Benchmark.input_generator import InputGenerator
from Benchmark.find_main import build_call_graph
from Benchmark.bench_mark_llm import LLMInputAnalyzer
from Benchmark.benchmark import (
    get_functions,
    BenchmarkEngine
)
load_dotenv()
GLOBAL_API_KEY = os.getenv("groq_api1")
class BenchmarkController:

    def __init__(
        self,
        code,
        max_n=10000,
        api_key=None
    ):
        self.code = code
        self.max_n = max_n
        self.api_key = api_key or GLOBAL_API_KEY

        if not self.api_key:
            raise ValueError("API Key for LLMInputAnalyzer was not found.")

    def generate_sizes(self):
        sizes = []
        if self.max_n <=500:
            return [
                50,
                100,
                150,
                min(250,self.max_n),
                self.max_n
            ]
            

        current = max(
            100,
            self.max_n // 16
        )

        while current <= self.max_n:
            sizes.append(current)
            current *= 2

        return sizes

    def run(self):
        from Benchmark.code_preprocess import (
            preprocess_code
        )

        clean_code = preprocess_code(
            self.code
        )
        functions = get_functions(clean_code)

        if not functions:
            raise ValueError("No top-level function found.")

        main_name = build_call_graph(clean_code)

        meta = None
        for func in functions:
            if func["name"] == main_name:
                meta = func
                break

        if meta is None:
            meta = functions[0]

        analyzer = LLMInputAnalyzer(api_key=self.api_key)
        schema = analyzer.analyze(
            code=clean_code,
            function_name=meta["name"],
            arguments=meta["args"]
        )
        print(schema)

        sizes = self.generate_sizes()
        results = []

        for size in sizes:
            generator = InputGenerator(schema, size)
            generated_input = generator.generate()

            bench = BenchmarkEngine(clean_code, generated_input)
            stats = bench.benchmark(meta["name"])

            results.append({
                "size": size,
                **stats
            })
            if stats["avg_time"]>=3:
                print("exiting early")
                break
                
            print(results)
        estimator = ComplexityEstimator()

        complexity = estimator.estimate(
            results
        )

        return {
            "main_function": meta,
            "schema": schema,
            "benchmarks": results,
            "complexity": complexity
        }


