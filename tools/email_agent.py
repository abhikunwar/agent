from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from tools.vision_tool import EmailVisionTool
from dotenv import load_dotenv
import os
import json

load_dotenv()


def create_email_agent():
    """Creates and returns Agent A — the email image reader agent."""

    llm = ChatOpenAI(
        model="gpt-5",
        temperature=0,
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )

    tools = [EmailVisionTool()]

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """You are an expert email data extraction agent.
Your only job is to extract all data fields and values from the email image provided.

Rules:
- Use the email_vision_tool to read the image
- Extract EVERY piece of data you see — numbers, names, dates, categories, codes
- Pay special attention to any category names like 'Direct CV', 'Direct EP', 
  'Direct Cardiology' or similar labels with associated values
- Return your final answer as a clean JSON object of all extracted fields
- Do not guess or add anything not visible in the image
- If a field has no clear name, label it as 'field_1', 'field_2' etc."""
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
        max_iterations=5
    )

    return agent_executor


def run_email_agent(image_path: str) -> dict:
    """Run Agent A on the email image and return extracted fields as dict."""

    agent = create_email_agent()

    result = agent.invoke({
        "input": f"Extract all data fields and values from this email image: {image_path}"
    })

    output = result.get("output", "{}")

    try:
        if "```json" in output:
            output = output.split("```json")[1].split("```")[0].strip()
        elif "```" in output:
            output = output.split("```")[1].split("```")[0].strip()
        return json.loads(output)
    except json.JSONDecodeError:
        return {"raw_output": output}