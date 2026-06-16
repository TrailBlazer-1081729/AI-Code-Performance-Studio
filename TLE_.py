import math
def normalize_complexity(complexity):
    return (
        str(complexity)
        .strip()
        .replace(" ", "")
        .replace("²", "^2")
        .replace("³", "^3")
        .replace("⁴", "^4")
        .replace("⁵", "^5")
        .replace("√", "sqrt")
        .lower()
    )
class TLEPredictor:

    def __init__(self, time_limit=1.0):
        self.time_limit = time_limit

    def calculate_factor(
        self,
        measured_n,
        target_n,
        complexity
    ):
        complexity = normalize_complexity(complexity)
        complexity = (
            complexity
            .strip()
            .replace(" ", "")
            .lower()
        )

        if measured_n <= 0 or target_n <= 0:
            raise ValueError(
                "Input sizes must be positive."
            )

        if complexity in [
            "o(1)",
            "constant"
        ]:
            return 1.0

        elif complexity in [
            "o(logn)",
            "logarithmic"
        ]:
            return (
                math.log2(target_n)
                /
                math.log2(measured_n)
            )

        elif complexity in [
            "o(log^2n)",
            "o(log2n)",
            "o(logn^2)"
        ]:
            return (
                math.log2(target_n) ** 2
            ) / (
                math.log2(measured_n) ** 2
            )

        elif complexity in [
            "o(sqrt(n))",
            "o(√n)"
        ]:
            return math.sqrt(
                target_n / measured_n
            )

        elif complexity in [
            "o(n)",
            "linear"
        ]:
            return (
                target_n
                /
                measured_n
            )

        elif complexity in [
            "o(nlogn)",
            "linearithmic"
        ]:
            return (
                target_n
                * math.log2(target_n)
            ) / (
                measured_n
                * math.log2(measured_n)
            )

        elif complexity in [
            "o(nlog^2n)",
            "o(nlog2n)"
        ]:
            return (
                target_n
                * (math.log2(target_n) ** 2)
            ) / (
                measured_n
                * (math.log2(measured_n) ** 2)
            )

        elif complexity in [
            "o(nsqrt(n))"
        ]:
            return (
                target_n
                * math.sqrt(target_n)
            ) / (
                measured_n
                * math.sqrt(measured_n)
            )

        elif complexity in [
            "o(n^2)",
            "o(n2)",
            "quadratic"
        ]:
            return (
                target_n
                /
                measured_n
            ) ** 2

        elif complexity in [
            "o(n^2logn)",
            "o(n2logn)"
        ]:
            return (
                (target_n ** 2)
                * math.log2(target_n)
            ) / (
                (measured_n ** 2)
                * math.log2(measured_n)
            )

        elif complexity in [
            "o(n^3)",
            "o(n3)",
            "cubic"
        ]:
            return (
                target_n
                /
                measured_n
            ) ** 3

        elif complexity in [
            "o(n^4)",
            "o(n4)"
        ]:
            return (
                target_n
                /
                measured_n
            ) ** 4

        elif complexity in [
            "o(n^5)",
            "o(n5)"
        ]:
            return (
                target_n
                /
                measured_n
            ) ** 5

        elif complexity in [
            "o(2^n)",
            "exponential"
        ]:
            exponent = (
                target_n
                - measured_n
            )

            if exponent > 1023:
                return float("inf")

            return 2 ** exponent

        elif complexity == "o(n!)":

            try:
                return (
                    math.factorial(target_n)
                    /
                    math.factorial(measured_n)
                )
            except OverflowError:
                return float("inf")

        elif complexity == "o(n^n)":

            try:
                return (
                    (target_n ** target_n)
                    /
                    (measured_n ** measured_n)
                )
            except OverflowError:
                return float("inf")

        raise ValueError(
            f"Unsupported complexity: {complexity}"
        )

    def predict(
        self,
        measured_time,
        measured_n,
        target_n,
        complexity
    ):
        try:

            factor = self.calculate_factor(
                measured_n,
                target_n,
                complexity
            )

            if (
                factor == float("inf")
                or
                math.isinf(factor)
            ):

                predicted_time = float("inf")
                risk = "🔴 VERY HIGH"

            else:

                predicted_time = (
                    measured_time
                    * factor
                )

                if (
                    predicted_time
                    < self.time_limit * 0.5
                ):
                    risk = "🟢 LOW"

                elif (
                    predicted_time
                    < self.time_limit
                ):
                    risk = "🟡 MODERATE"

                elif (
                    predicted_time
                    < self.time_limit * 3
                ):
                    risk = "🟠 HIGH"

                else:
                    risk = "🔴 VERY HIGH"

            return {
                "measured_n":
                    measured_n,

                "target_n":
                    target_n,

                "predicted_runtime_sec":
                    predicted_time,

                "risk_level":
                    risk,

                "estimated_slowdown":
                    factor
            }

        except Exception as e:

            return {
                "measured_n":
                    measured_n,

                "target_n":
                    target_n,

                "predicted_runtime_sec":
                    float("inf"),

                "risk_level":
                    "🔴 ERROR",

                "estimated_slowdown":
                    0.0,

                "error":
                    str(e)
            }