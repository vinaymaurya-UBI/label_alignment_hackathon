"""
Check if the drug_ra database exists and has data.
Run from project root: uv run python scripts/check_db_data.py
"""
import os
import sqlite3
import sys

# Possible DB locations (relative to project root and to backend/)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CANDIDATES = [
    os.path.join(PROJECT_ROOT, "data", "drug_ra.db"),
    os.path.join(PROJECT_ROOT, "backend", "data", "drug_ra.db"),
]


def check_db(path: str) -> dict | None:
    if not os.path.isfile(path):
        return None
    try:
        conn = sqlite3.connect(path)
        cur = conn.cursor()
        tables = ["drugs", "drug_labels", "label_sections", "regulatory_authorities"]
        counts = {}
        for table in tables:
            try:
                cur.execute(f"SELECT COUNT(*) FROM {table}")
                counts[table] = cur.fetchone()[0]
            except sqlite3.OperationalError:
                counts[table] = "table missing"
        conn.close()
        return counts
    except Exception as e:
        return {"error": str(e)}


def main():
    print("Database path check (from project root:", PROJECT_ROOT, ")\n")
    found = False
    for path in CANDIDATES:
        rel = os.path.relpath(path, PROJECT_ROOT)
        print(f"  {rel}: ", end="")
        result = check_db(path)
        if result is None:
            print("file not found")
            continue
        found = True
        if "error" in result:
            print("ERROR:", result["error"])
            continue
        print("found")
        for table, count in result.items():
            print(f"    {table}: {count}")
        total_drugs = result.get("drugs", 0)
        if isinstance(total_drugs, int) and total_drugs == 0:
            print("\n  -> Database is empty. Populate with:")
            print("     uv run python scripts/populate_all_countries_real_data.py")
        print()
    if not found:
        print("No drug_ra.db found at any candidate path.")
        print("The API creates an empty DB on first run. To add data, run:")
        print("  uv run python scripts/populate_all_countries_real_data.py")
        print("\nNote: DATABASE_URL in .env is sqlite+aiosqlite:///./data/drug_ra.db")
        print("If you start the server from backend/, the DB is at backend/data/drug_ra.db")
        sys.exit(1)


if __name__ == "__main__":
    main()
