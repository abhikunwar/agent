import json
from agents.excel_agent import run_excel_agent, run_excel_agent_bulk

print("=== AGENT B: Excel Reasoning Agent ===\n")

print("--- Test 1: Single field lookup ---")
result = run_excel_agent(
    excel_path="inputs/source.xlsx",
    field="Direct CV",       # change to real category in your Excel
    value="5000"             # change to real value in your Excel
)
print("\nResult:")
print(json.dumps(result, indent=2))

print("\n--- Test 2: Bulk lookup (multiple fields) ---")
# Simulate what Agent A would return from the email
mock_email_fields = {
    "Direct CV": "5000",
    "Direct EP": "3200",
    "Direct Cardiology": "1500"
}

bulk_result = run_excel_agent_bulk(
    excel_path="inputs/source.xlsx",
    extracted_fields=mock_email_fields
)
print("\nBulk Result:")
print(json.dumps(bulk_result, indent=2))