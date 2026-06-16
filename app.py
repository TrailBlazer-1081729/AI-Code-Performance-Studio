import time

import gradio as gr
import ast_file as a
import pandas as pd
from tle_controller import TLEController
from final_report import generate_report

with gr.Blocks() as demo:
    gr.Markdown("# AI Code Performance Studio")
    with gr.Tabs():
        # TAB 1
        with gr.Tab("Complexity Analysis"):
            code_input = gr.Textbox(
                label="Python Code",
                lines=25,
                max_lines=40,
                placeholder="Paste your code here..."
            )
            analyze_btn = gr.Button(
                "Analyze Complexity",
                variant="primary"
            )

            with gr.Row():

                with gr.Column(scale=1):
                    ast_output = gr.JSON(
                        label="AST Summary"
                    )

                with gr.Column(scale=2):
                    complexity_output = gr.Markdown(
                        label="Complexity Analysis"
                    )

            analyze_btn.click(
                fn=a.analyze_complexity,
                inputs=[code_input],
                outputs=[
                    ast_output,
                    complexity_output
                ]
            )

        # TAB 2
        with gr.Tab("Benchmarking"):
            benchmark_code = gr.Textbox(
                lines=20,
                label="Python Code"
            )
            max_n = gr.Slider(
                minimum=100,
                maximum=40000,
                value=10000,
                step=100,
                label="Maximum Input Size"
            )
            benchmark_btn = gr.Button(
                "Run Benchmark",
                variant="primary"
            )
            schema_output = gr.JSON(
                label="Detected Input Schema"
            )

            benchmark_output = gr.Dataframe(
                headers=[
                    "Size",
                    "Avg Time",
                    "Median Time",
                    "Best Time",
                    "Worst Time",
                    "Peak Memory (KB)"
                ],
                label="Benchmark Results"
            )

            runtime_plot = gr.LinePlot(
                x="size",
                y="avg_time",
                title="Runtime Growth"
            )

            memory_plot = gr.LinePlot(
                x="size",
                y="peak_memory_kb",
                title="Memory Growth"
            )

            complexity_output = gr.Markdown(
                label="Observed Complexity"
            )

            insights_output = gr.Markdown(
                label="AI Insights"
            )

            from Benchmark.Benchmark_controller import (
                BenchmarkController
            )


            def run_benchmark_pipeline(code, max_n):
                try:
                    controller = BenchmarkController(
                        code=code,
                        max_n=max_n
                    )
                    result = controller.run()
                except ValueError as e:
                    msg = str(e)
                    if "No top-level function found" in msg:
                        return (
                            {},
                            [],
                            pd.DataFrame(),
                            pd.DataFrame(),
                            "# Benchmark Unavailable",
                            """
                ### Benchmark Status
                No benchmarkable function was found.
                Examples:
                def solve(nums):
                    return sum(nums)

                or

                def binary_search(arr, target):
                    ...
                """

                        )
                    elif "Unsupported type" in msg:
                        return (
                            {},
                            [],
                            pd.DataFrame(),
                            pd.DataFrame(),
                            "# Benchmark Unavailable",
                            f"""
                ### Benchmark Status
                Detected unsupported input type.
                **Details:** {msg}
                Currently supported:
                - int
                - float
                - str
                - list[int]
                - list[float]
                - list[str]
                Coming soon:
                - ListNode
                - TreeNode
                - GraphNode
                - Custom data structures
                """
                        )
                    raise
                except Exception as e:
                    return (
                        {},
                        [],
                        pd.DataFrame(),
                        pd.DataFrame(),
                        "# Benchmark Failed",
                        f"### Error\n{type(e).__name__}: {e}"
                    )
                table_rows = []
                for item in result["benchmarks"]:
                    table_rows.append(
                        [
                            item["size"],
                            item["avg_time"],
                            item["median_time"],
                            item["best_time"],
                            item["worst_time"],
                            item["peak_memory_kb"]
                        ]
                    )

                benchmark_df = pd.DataFrame(
                    result["benchmarks"]
                )

                peak_memory = max(
                    item["peak_memory_kb"]
                    for item in result["benchmarks"]
                )

                insights = f"""
            ###  Performance Insights
            **Observed Complexity:** {result["complexity"]}
            **Peak Memory Usage:** {peak_memory:.2f} KB
            **Benchmark Samples:** {len(result["benchmarks"])}
            **Status:** Benchmark completed successfully.
            """

                return (
                    result["schema"],
                    table_rows,
                    benchmark_df,
                    benchmark_df,
                    f"# {result['complexity']}",
                    insights
                )


            benchmark_btn.click(
                fn=run_benchmark_pipeline,
                inputs=[
                    benchmark_code,
                    max_n
                ],
                outputs=[
                    schema_output,
                    benchmark_output,
                    runtime_plot,
                    memory_plot,
                    complexity_output,
                    insights_output
                ]
            )

        # TAB 3
        import textwrap
        with gr.Tab("TLE_FINDER"):

            perf_code = gr.Textbox(
                label="Python Code",
                lines=20
            )
            constraint = gr.Textbox(
                label="Constraint",
                value="5000",
                placeholder="n <= 100000"
            )

            tle_btn = gr.Button(
                    "Estimate TLE Risk",
                    variant="primary"
                )
            analysis_output = gr.Markdown( min_height=500)
            def run_tle_analysis(code, constraint):
                try:

                    controller = TLEController(
                        code=code,
                        constraint=constraint
                    )
                    yield (
                        "# ⏳ Running Analysis\n\nAnalyzing code and benchmarking performance..."
                    )
                    result = controller.run()

                    yield (
                        "# ⏳ Runtime Prediction\n\nEstimating scalability and TLE risk..."
                    )
                    prediction = result["prediction"]
                    runtime = prediction["predicted_runtime_sec"]
                    if runtime == float("inf"):
                        runtime_text = "∞"
                    else:
                        runtime_text = f"{runtime:.6f} sec"

                    risk = prediction["risk_level"]

                    if "LOW" in risk:
                        verdict_text = "Expected to pass comfortably."
                    elif "MODERATE" in risk:
                        verdict_text = "Close to the time limit."
                    elif "HIGH" in risk:
                        verdict_text = "Optimization recommended."
                    else:
                        verdict_text = "Very likely to exceed the time limit."

                    report = textwrap.dedent(f"""
                    # 🚦 TLE Risk Analysis

                    ## Complexity Assessment

                    | Source | Complexity |
                    |----------|----------|
                    | AST Analysis | {result["ast_complexity"]} |
                    | Benchmark Analysis | {result["benchmark_complexity"]} |
                    | Final Complexity Used | {result["chosen_complexity"]} |

                    **Confidence:** {result["confidence"]}

                    ---

                    ## Runtime Projection

                    | Metric | Value |
                    |----------|----------|
                    | Measured Input Size | {prediction["measured_n"]:,} |
                    | Target Input Size | {prediction["target_n"]:,} |
                    | Estimated Slowdown | {prediction["estimated_slowdown"]:.2f}x |
                    | Predicted Runtime | {runtime_text} |

                    ---

                    ## Verdict

                    ### {prediction["risk_level"]}

                    {verdict_text}
                    """)

                    yield report
                    print("com")


                except Exception as e:

                    error_report = textwrap.dedent(f"""
                    # ❌ Analysis Failed

                    ```text
                    {str(e)}
                    ```
                    """)

                    yield error_report
                finally:
                    print("GENERATOR CLOSED")


            run_event = tle_btn.click(
                fn=run_tle_analysis,
                inputs=[perf_code, constraint],
                outputs=[analysis_output],
                show_progress="full"
            )


            def show_cancel_message():
                return (
                    """
            # 🛑 Analysis Cancelled

            The current TLE analysis was cancelled by the user.

            You can modify the code and start a new analysis.
                    """
                )


            cancel_btn = gr.Button("🛑 Cancel")

            cancel_btn.click(
                fn=None,
                cancels=[run_event]
            )

            cancel_btn.click(
                fn=show_cancel_message,
                outputs=[
                    analysis_output
                ],
                queue=False
            )


        with gr.Tab("AI Performance Report"):
            report_code = gr.Textbox(
                label="Python Code",
                lines=20
            )

            report_constraint = gr.Textbox(
                label="Constraint",
                value="5000",
                placeholder="n <= 100000"
            )

            generate_btn = gr.Button(
                "Generate Report",
                variant="primary"
            )
            cancel_report_btn = gr.Button(
                "🛑 Cancel Report"
            )

            report_output = gr.Markdown(min_height=500)


            def generate_full_report(code, constraint):
                try:
                    yield "# ⏳ Running AST analysis..."

                    controller = TLEController(
                        code=code,
                        constraint=constraint
                    )

                    tle_result = controller.run()

                    yield "# ⏳ Generating AI report..."

                    report = generate_report(tle_result)

                    yield report

                except Exception as e:
                    yield f"""
            # ❌ Report Generation Failed

            {type(e).__name__}: {e}
            """


            def show_report_cancel_message():
                return """
            # 🛑 Report Generation Cancelled

            The report generation process was cancelled.

            You can modify the code and generate a new report.
            """


            report_event = generate_btn.click(
                fn=generate_full_report,
                inputs=[
                    report_code,
                    report_constraint
                ],
                outputs=[
                    report_output
                ],
                show_progress="full"
            )
            cancel_report_btn.click(
                fn=None,
                cancels=[report_event]
            )

            cancel_report_btn.click(
                fn=show_report_cancel_message,
                outputs=[report_output],
                queue=False
            )


if __name__ == "__main__":
    demo.launch()
