import math


class ComplexityEstimator:

    def estimate(
        self,
        benchmarks
    ):

        exponents = []

        for i in range(
            len(benchmarks) - 1
        ):

            s1 = benchmarks[i]["size"]
            s2 = benchmarks[i + 1]["size"]

            t1 = benchmarks[i]["avg_time"]
            t2 = benchmarks[i + 1]["avg_time"]

            if (
                s1 <= 0
                or s2 <= 0
                or t1 <= 0
                or t2 <= 0
            ):
                continue

            exponent = (
                math.log(
                    t2 / t1
                )
                /
                math.log(
                    s2 / s1
                )
            )

            exponents.append(
                exponent
            )

        if not exponents:
            return "Unable to Estimate"

        avg = (
            sum(exponents)
            /
            len(exponents)
        )

        if avg < 0.3:
            return "O(1)"

        elif avg < 1.3:
            return "O(n)"

        elif avg < 1.7:
            return "O(n log n)"

        elif avg < 2.3:
            return "O(n²)"

        elif avg < 3.3:
            return "O(n³)"

        return "Exponential or Higher"