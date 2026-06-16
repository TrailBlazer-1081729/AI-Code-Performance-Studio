import random
import string


class InputGenerator:

    def __init__(self, schema, size=100):
        self.schema = schema
        self.size = size
    def _generate_value(
        self,
        param_type,
        scales_with_n
    ):
        param_type = (
            param_type
            .replace(" ", "")
            .lower()
        )
        length = (
            self.size
            if scales_with_n
            else 10
        )
        if param_type == "int":
            return (
                self.size
                if scales_with_n
                else random.randint(
                    1,
                    100
                )
            )

        if param_type == "float":

            upper = (
                float(self.size)
                if scales_with_n
                else 100.0
            )

            return random.uniform(
                1.0,
                upper
            )

        if param_type == "bool":
            return random.choice(
                [True, False]
            )

        if param_type == "str":

            return "".join(
                random.choices(
                    string.ascii_lowercase,
                    k=length
                )
            )

        if param_type == "list":

            return [
                random.randint(
                    1,
                    self.size
                )
                for _ in range(length)
            ]

        if param_type == "list[int]":

            return [
                random.randint(
                    1,
                    self.size
                )
                for _ in range(length)
            ]

        if param_type == "list[float]":

            return [
                random.uniform(
                    1.0,
                    float(self.size)
                )
                for _ in range(length)
            ]

        if param_type == "list[str]":

            return [
                "".join(
                    random.choices(
                        string.ascii_lowercase,
                        k=5
                    )
                )
                for _ in range(length)
            ]

        if param_type == "set":

            return {
                random.randint(
                    1,
                    self.size * 3
                )
                for _ in range(length)
            }

        if param_type == "set[int]":

            return {
                random.randint(
                    1,
                    self.size * 3
                )
                for _ in range(length)
            }

        if param_type == "set[str]":

            generated = set()

            while len(generated) < length:

                generated.add(
                    "".join(
                        random.choices(
                            string.ascii_lowercase,
                            k=5
                        )
                    )
                )

            return generated

        if param_type == "tuple":

            return (
                random.randint(
                    1,
                    100
                ),
                random.randint(
                    1,
                    100
                )
            )

        if param_type == "dict":

            return {
                f"key_{i}":
                random.randint(
                    1,
                    100
                )
                for i in range(length)
            }

        if param_type == "dict[str,int]":

            return {
                f"key_{i}":
                random.randint(
                    1,
                    100
                )
                for i in range(length)
            }

        if param_type == "dict[int,int]":

            return {
                i:
                random.randint(
                    1,
                    100
                )
                for i in range(length)
            }

        if param_type == "list[list[int]]":

            dimension = (
                max(
                    2,
                    int(
                        self.size ** 0.5
                    )
                )
                if scales_with_n
                else 3
            )

            return [
                [
                    random.randint(
                        1,
                        100
                    )
                    for _ in range(
                        dimension
                    )
                ]
                for _ in range(
                    dimension
                )
            ]

        if param_type == "dict[int,list[int]]":

            graph = {}

            nodes_count = (
                self.size
                if scales_with_n
                else 5
            )

            for i in range(
                nodes_count
            ):

                possible = [
                    node
                    for node in range(
                        nodes_count
                    )
                    if node != i
                ]

                edges_count = (
                    random.randint(
                        0,
                        min(
                            5,
                            len(possible)
                        )
                    )
                )

                graph[i] = (
                    random.sample(
                        possible,
                        edges_count
                    )
                )

            return graph

        raise ValueError(
            f"Unsupported type: {param_type.lower()}"
        )

    def generate(self):

        args = []

        for param in (
            self.schema[
                "parameters"
            ]
        ):

            args.append(
                self._generate_value(
                    param["type"],
                    param[
                        "scales_with_n"
                    ]
                )
            )

        return tuple(args)


