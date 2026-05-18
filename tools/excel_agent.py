from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from tools.excel_tool import ExcelSchemaTool, ExcelLookupTool
from dotenv import load_dotenv
import os
import json

load_dotenv()


def create_excel_agent():
    """Creates and returns Agent B — the smart Excel reasoning agent."""

    llm = ChatOpenAI(
        model="gpt-5",
        temperature=0,
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )

    tools = [ExcelSchemaTool(), ExcelLookupTool()]

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """You are an expert Excel data reasoning agent.
You deeply understand complex Excel files where:
- Column A contains category labels like 'Direct CV', 'Direct EP', 'Direct Cardiology' etc.
- Other columns contain values, descriptions, amounts, or metadata for each category
- Data may be spread across multiple sheets
- Column headers may not be on row 1 — they could be anywhere

Your job when given a field and value to search:
1. First use excel_schema_tool to fully understand the Excel structure
2. Then use excel_lookup_tool to find the specific field and value
3. Reason semantically — 'Direct CV' and 'direct cv' should be treated as same
4. If exact value not found, check for close matches or partial matches
5. Always return a detailed JSON with your findings

Never guess. Only report what you actually find in the Excel."""
        ),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])

    agent = create_openai_tools_agent(
        llm=llm,
        tools=tools,
        prompt=prompt
    )

    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=8
    )

    return agent_executor


def run_excel_agent(excel_path: str, field: str, value: str) -> dict:
    """
    Run Agent B to find a specific field+value in the Excel.
    Returns a dict with match result, location, and notes.
    """

    agent = create_excel_agent()

    query = (
        f"Search the Excel file at '{excel_path}'. "
        f"I am looking for the field/category '{field}' with value '{value}'. "
        f"First understand the Excel structure, then find if this field and value exist. "
        f"Return a detailed JSON with: matched, sheet, row, column, "
        f"excel_value, searched_value, category, notes."
    )

    result = agent.invoke({"input": query})

    output = result.get("output", "{}")

    try:
        if "```json" in output:
            output = output.split("```json")[1].split("```")[0].strip()
        elif "```" in output:
            output = output.split("```")[1].split("```")[0].strip()
        return json.loads(output)
    except json.JSONDecodeError:
        return {"raw_output": output}


def run_excel_agent_bulk(excel_path: str, extracted_fields: dict) -> list:
    """
    Run Agent B for ALL fields extracted from the email at once.
    Returns a list of match results — one per field.
    """

    agent = create_excel_agent()

    fields_text = json.dumps(extracted_fields, indent=2)

    query = (
        f"Search the Excel file at '{excel_path}'. "
        f"Here are ALL the fields and values extracted from an email:\n{fields_text}\n\n"
        f"For EACH field-value pair: "
        f"1. Understand the Excel structure first "
        f"2. Search for that field and value "
        f"3. Report if it matched, where it is, and any differences "
        f"Return a JSON array, one result object per field like: "
        f'[{{"field": "Direct CV", "value": "5000", "matched": true, '
        f'"sheet": "Sheet1", "row": 3, "column": "B", '
        f'"excel_value": "5000", "notes": "exact match"}}]'
    )

    result = agent.invoke({"input": query})
    output = result.get("output", "[]")

    try:
        if "```json" in output:
            output = output.split("```json")[1].split("```")[0].strip()
        elif "```" in output:
            output = output.split("```")[1].split("```")[0].strip()
        return json.loads(output)
    except json.JSONDecodeError:
        return [{"raw_output": output}]