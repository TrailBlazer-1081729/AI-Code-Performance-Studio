import json
from groq import Groq


class LLMInputAnalyzer:

    def __init__(self, api_key):
        self.client = Groq(
            api_key=api_key
        )

    def analyze(
        self,
        code,
        function_name,
        arguments
    ):

        prompt = f"""
You are a Python parameter inference engine.

Analyze ONLY the target function.

Return ONLY valid JSON.

SUPPORTED_TYPES = {
    "int",
    "float",
    "bool",
    "str",
    "list",
    "list[int]",
    "list[float]",
    "list[str]",
    "list[list[int]]",
    "set",
    "set[int]",
    "set[str]",
    "dict",
    "dict[str,int]",
    "dict[int,int]",
    "dict[int,list[int]]",
    "tuple"
}

Function Name:
{function_name}

Arguments:
{arguments}

Code:
{code}

Return exactly:

{{
    "function_name": "{function_name}",
    "parameters": [
        {{
            "name": "",
            "type": "",
            "scales_with_n": true
        }}
    ]
}}
"""
        print("CALLING COMPLEXITY ANALYZER")
        response = (
            self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content":
                        "Return only valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0
            )
        )

        content = (
            response
            .choices[0]
            .message
            .content
            .strip()
        )

        if content.startswith("```json"):
            content = (
                content
                .replace(
                    "```json",
                    ""
                )
                .replace(
                    "```",
                    ""
                )
                .strip()
            )

        return json.loads(content)