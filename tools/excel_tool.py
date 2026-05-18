import pandas as pd
from langchain.tools import BaseTool
from openai import OpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def load_excel_schema(file_path: str) -> dict:
    """Read all sheets and build a full schema understanding of the Excel file."""
    xl = pd.ExcelFile(file_path)
    schema = {}

    for sheet_name in xl.sheet_names:
        df = xl.parse(sheet_name, header=None)
        schema[sheet_name] = {
            "shape": df.shape,
            "preview": df.to_string(max_rows=50, max_cols=20)
        }

    return schema


def ask_gpt_about_excel(schema: dict, question: str) -> str:
    """Send the Excel schema + a question to GPT-5 for semantic reasoning."""

    schema_text = ""
    for sheet, info in schema.items():
        schema_text += f"\n--- Sheet: {sheet} ---\n"
        schema_text += f"Size: {info['shape'][0]} rows x {info['shape'][1]} cols\n"
        schema_text += f"Content preview:\n{info['preview']}\n"

    response = client.chat.completions.create(
        model="gpt-5",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an Excel data expert. You understand complex Excel files "
                    "where column A contains category labels like 'Direct CV', 'Direct EP', "
                    "'Direct Cardiology' etc. and other columns contain corresponding values. "
                    "You can reason about the structure semantically, not just by exact cell lookup. "
                    "Always return answers as valid JSON only. No markdown, no explanation."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Here is the full Excel file content:\n{schema_text}\n\n"
                    f"Question: {question}"
                )
            }
        ],
        max_tokens=1500
    )

    return response.choices[0].message.content.strip()


class ExcelSchemaTool(BaseTool):
    name: str = "excel_schema_tool"
    description: str = (
        "Use this tool to understand the structure and schema of the Excel file. "
        "Input must be the full path to the Excel file. "
        "Returns a JSON summary of all sheets, column A categories, and data layout."
    )
    file_path: str = ""

    def _run(self, file_path: str) -> str:
        try:
            schema = load_excel_schema(file_path.strip())
            question = (
                "Analyze this Excel file structure. "
                "Identify all category labels in column A (like Direct CV, Direct EP etc). "
                "For each category, identify what columns hold values and what those columns mean. "
                "Return JSON like: "
                '{"categories": ["Direct CV", "Direct EP"], '
                '"structure": {"col_A": "category labels", "col_B": "description of col B"}, '
                '"sheet_names": ["Sheet1"]}'
            )
            result = ask_gpt_about_excel(schema, question)
            return result
        except Exception as e:
            return json.dumps({"error": str(e)})

    async def _arun(self, file_path: str) -> str:
        raise NotImplementedError("Async not supported")


class ExcelLookupTool(BaseTool):
    name: str = "excel_lookup_tool"
    description: str = (
        "Use this tool to search for a specific field and value inside the Excel file. "
        "Input must be a JSON string with keys: 'file_path', 'field', 'value'. "
        "Example: '{\"file_path\": \"inputs/source.xlsx\", "
        "\"field\": \"Direct CV\", \"value\": \"5000\"}' "
        "Returns match result with sheet name, row, and column location."
    )

    def _run(self, input_str: str) -> str:
        try:
            params = json.loads(input_str)
            file_path = params.get("file_path", "inputs/source.xlsx")
            field = params.get("field", "")
            value = params.get("value", "")

            schema = load_excel_schema(file_path)

            question = (
                f"I am looking for the field '{field}' with value '{value}'. "
                f"Search through the Excel content and tell me: "
                f"1. Does this field and value exist? "
                f"2. Which sheet is it in? "
                f"3. Which row number? "
                f"4. Which column? "
                f"5. What is the exact value in Excel vs what I searched for? "
                f"Return JSON like: "
                f'{{"matched": true, "sheet": "Sheet1", "row": 3, "column": "B", '
                f'"excel_value": "5000", "searched_value": "5000", '
                f'"category": "Direct CV", "notes": "exact match"}}'
            )

            result = ask_gpt_about_excel(schema, question)
            return result

        except Exception as e:
            return json.dumps({"error": str(e)})

    async def _arun(self, input_str: str) -> str:
        raise NotImplementedError("Async not supported")