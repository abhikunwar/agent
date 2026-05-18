import os
import json
import pandas as pd
from datetime import datetime
from agents.email_agent import run_email_agent
from agents.excel_agent import run_excel_agent_bulk


def print_banner():
    print("=" * 60)
    print("   EMAIL vs EXCEL VERIFICATION AGENT")
    print("   Powered by LangChain + GPT-5")
    print("=" * 60)


def main():
    # ── inputs ──────────────────────────────────────────────
    image_path = "inputs/email.png"
    excel_path = "inputs/source.xlsx"

    print_banner()
    print(f"\n📧 Email image  : {image_path}")
    print(f"📊 Excel source : {excel_path}")

    # ── STEP 1: Agent A — extract fields from email image ───
    print("\n🔍 Step 1: Extracting data from email image...")
    extracted_fields = run_email_agent(image_path)

    print("\n📋 Extracted fields from email:")
    for key, value in extracted_fields.items():
        print(f"   {key}: {value}")

    # ── STEP 2: Agent B — verify each field against Excel ───
    print("\n🔍 Step 2: Verifying fields against Excel...")
    verification_results = run_excel_agent_bulk(
        excel_path=excel_path,
        extracted_fields=extracted_fields
    )

    # ── STEP 3: Build DataFrame ──────────────────────────────
    print("\n📊 Step 3: Building result DataFrame...")
    rows = []
    for item in verification_results:
        rows.append({
            "field":          item.get("field", ""),
            "email_value":    item.get("value", ""),
            "excel_value":    item.get("excel_value", ""),
            "matched":        item.get("matched", False),
            "sheet":          item.get("sheet", ""),
            "row":            item.get("row", ""),
            "column":         item.get("column", ""),
            "notes":          item.get("notes", "")
        })

    df = pd.DataFrame(rows)

    # ── STEP 4: Save to CSV ──────────────────────────────────
    os.makedirs("output", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"output/result_{timestamp}.csv"
    df.to_csv(output_path, index=False)

    # ── STEP 5: Print summary ────────────────────────────────
    print("\n" + "=" * 60)
    print("         VERIFICATION RESULTS")
    print("=" * 60)
    print(df.to_string(index=False))

    total     = len(df)
    matched   = df["matched"].sum()
    mismatched = total - matched

    print("\n" + "=" * 60)
    print(f"  Total fields  : {total}")
    print(f"  ✅ Matched    : {matched}")
    print(f"  ❌ Mismatched : {mismatched}")

    if mismatched == 0:
        print("\n  Verdict: ✅ FULL MATCH")
    elif matched == 0:
        print("\n  Verdict: ❌ NO MATCH")
    else:
        print("\n  Verdict: ⚠️  PARTIAL MATCH")

    print("=" * 60)
    print(f"\n💾 CSV saved to: {output_path}")


if __name__ == "__main__":
    main()