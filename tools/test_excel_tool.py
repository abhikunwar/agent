import json
from tools.excel_tool import ExcelSchemaTool, ExcelLookupTool

print("=== TEST 1: Understanding Excel Structure ===")
schema_tool = ExcelSchemaTool()
schema_result = schema_tool._run("inputs/source.xlsx")

print("\nExcel Schema Understanding:")
try:
    parsed = json.loads(schema_result)
    print(json.dumps(parsed, indent=2))
except:
    print(schema_result)

print("\n")
print("=== TEST 2: Lookup a Specific Field & Value ===")

lookup_tool = ExcelLookupTool()

# Edit these two values to match something you expect in your Excel
test_field = "Direct CV"   # <-- change this to a real category from your Excel
test_value = "5000"        # <-- change this to a real value from your Excel

lookup_input = json.dumps({
    "file_path": "inputs/source.xlsx",
    "field": test_field,
    "value": test_value
})

lookup_result = lookup_tool._run(lookup_input)

print(f"\nSearching for field='{test_field}' value='{test_value}':")
try:
    parsed = json.loads(lookup_result)
    print(json.dumps(parsed, indent=2))
except:
    print(lookup_result)