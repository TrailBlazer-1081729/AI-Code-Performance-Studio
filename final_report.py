import math
import os
from dotenv import load_dotenv
from openai import OpenAI


def benchmark_to_markdown(benchmarks):
    if not benchmarks:
        return "No benchmark data available."

    rows = [
        "| N | Avg Runtime (s) | Peak Memory (KB) |",
        "|---|---|---|",
    ]

    for b in benchmarks:
        avg_time = b.get("avg_time", 0)
        time_str = format_runtime(avg_time)
        if time_str != "Infinity" and isinstance(avg_time, (int, float)):
            time_str = f"{avg_time:.6f}"

        rows.append(
            f"| {b.get('size','N/A')} "
            f"| {time_str} "
            f"| {b.get('peak_memory_kb',0):.2f} |"
        )

    return "\n".join(rows)


def format_runtime(value):
    if isinstance(value, (int, float)):
        if math.isinf(value):
            return "Infinity"
        return f"{value:.6f}"
    if str(value).lower() in ("inf", "infinity"):
        return "Infinity"
    return str(value)

def generate_report(tle_result):
    load_dotenv()

    client = OpenAI(
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        api_key=os.getenv("google_key"),
        timeout=60,
    )

    prediction = tle_result.get("prediction", {})
    benchmark_data = tle_result.get("benchmark_result", {})
    benchmarks = benchmark_data.get("benchmarks", [])

    ast_complexity = tle_result.get("ast_complexity", "Unknown")
    benchmark_complexity = tle_result.get("benchmark_complexity", "Unknown")
    selected_complexity = tle_result.get("chosen_complexity", "Unknown")
    confidence = tle_result.get("confidence", "Unknown")

    agreement = "Yes" if ast_complexity == benchmark_complexity else "No"
    sample_count = len(benchmarks)

    peak_memory = (
        max(b.get("peak_memory_kb", 0) for b in benchmarks) if benchmarks else 0
    )
    max_runtime = (
        max(b.get("avg_time", 0) for b in benchmarks) if benchmarks else 0
    )

    benchmark_table = benchmark_to_markdown(benchmarks)

    system_prompt = """You are a Senior Software Performance Engineer.
Your task is to generate a professional engineering report from analysis results that have ALREADY been computed by the system.

CRITICAL RULES:
1. All supplied metrics are authoritative system outputs. Never change, replace, or override supplied values.
2. Treat Selected Complexity as the final complexity. If Selected Complexity differs from Benchmark Complexity, Selected Complexity takes precedence.
3. Do not perform your own independent complexity analysis of source code.
4. Do not invent benchmark results, runtime values, memory values, or constraints not supported by provided data.
5. Never use LaTeX or mathematical notation blocks.

WHEN AST AND BENCHMARK DISAGREE:
If AST complexity and benchmark complexity differ, explicitly state that a discrepancy exists:
- Explain that empirical benchmarks reflect observed behavior on tested inputs.
- Explain that static analysis reflects structural characteristics of the implementation.
- State that the system selected the final complexity shown in the Selected Complexity field. Do not choose a different complexity.

OUTPUT STYLE:
Generate a complete engineering performance report in GitHub-flavored Markdown using professional language, clean headers, and concise bullet points.
"""

    user_prompt = f"""Authoritative Analysis Results

Complexity
- AST Complexity: {ast_complexity}
- Benchmark Complexity: {benchmark_complexity}
- Selected Complexity (Final): {selected_complexity}
- Confidence: {confidence}
- Analysis Agreement: {agreement}

---

Runtime Prediction
- Risk Level: {prediction.get("risk_level")}
- Predicted Runtime: {format_runtime(prediction.get("predicted_runtime_sec"))}
- Estimated Slowdown: {prediction.get("estimated_slowdown")}
- Measured N: {prediction.get("measured_n")}
- Target N: {prediction.get("target_n")}

---

Benchmark Summary
- Benchmark Samples: {sample_count}
- Peak Memory: {peak_memory:.2f} KB
- Max Runtime: {format_runtime(max_runtime)}

Benchmark Table
{benchmark_table}

---

Generate a professional engineering report with these sections:

# Executive Summary
Provide a concise, high-level summary of performance characteristics using the supplied engine metrics.

# Complexity Analysis
Discuss the AST complexity, Benchmark complexity, Selected complexity, and Confidence level. Explicitly reference the provided Analysis Agreement value ({agreement})—do not determine agreement independently. Use the provided Analysis Agreement value.

# Benchmark Findings
Analyze runtime growth, memory growth, and scalability trends using exclusively the data present in the Benchmark Table. Note that exactly {sample_count} samples were collected.

# Runtime Scalability
Discuss scalability only to the extent supported by the selected complexity and benchmark evidence. Explicitly state when projections are estimates.

# Memory Usage
Evaluate peak memory observations, footprint allocation efficiency, and scalability boundaries.

# TLE Risk Assessment
Analyze the Risk Level, Predicted Runtime, and Expected Slowdown against typical competitive programming limitations. The Risk Level shown above is a final system output. Do not recalculate risk.

# Optimization Recommendations
Provide ordered engineering suggestions aligned structurally with the Selected Complexity. Explain expected impact based on supplied evidence.
"""

    total_chars = len(system_prompt) + len(user_prompt)
    print("PROMPT CHARS:", total_chars)
    print("EST TOKENS:", total_chars // 4)

    try:
        print("BEFORE API")
        response = client.chat.completions.create(
            model="gemini-3.1-flash-lite",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        print("AFTER API")
        return response.choices[0].message.content
    except Exception as e:
        print("API ERROR:", repr(e))
        raise
