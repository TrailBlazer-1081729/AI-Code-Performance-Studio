import os
from Benchmark.Benchmark_controller import BenchmarkController

# An advanced scheduling/dependency algorithm
dependency_code = """
class Solution:
    def mapWordWeights(self, words: List[str], weights: List[int]) -> str:
        ans = []

        for word in words:
            total = 0

            for ch in word:
                total += weights[ord(ch) - ord('a')]

            remainder = total % 26
            ans.append(chr(ord('z') - remainder))

        return "".join(ans)

"""

if not os.getenv("groq_api1"):
    os.environ["groq_api1"] = "your_actual_groq_api_key_here"

controller = BenchmarkController(
    code=dependency_code,
    max_n=5000
)

try:
    print("Launching multi-parameter dependency analysis pipeline...")
    performance_results = controller.run()

    print("\n=== BENCHMARK RESULTS ===")
    print(f"Generated Schema: {performance_results['schema']}")

    for report in performance_results["benchmarks"]:
        print(f"\n[Data Scale Size: {report['size']}]")
        print(f"  Target Entry Function : {report['function_name']}")
        print(f"  Average Runtime       : {report['avg_time']} seconds")
        print(f"  Peak Memory Overhead  : {report['peak_memory_kb']} KB")
        print(f"  Execution Profiles    : {report['runs']} runs monitored")

except Exception as e:
    print(f"\nPipeline Execution Failed: {e}")