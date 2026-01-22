from pathlib import Path

FILES = {
    "file1_basic.csv": """id,name,age,city
1,Alice,30,Dublin
2,Bob,25,Cork
3,Charlie,35,Galway
""",
    "file2_basic.csv": """id,name,age,city
1,Alice,31,Dublin
2,Bob,25,Cork
3,Charlie,35,Galway
4,Diana,28,Limerick
""",
    "file1_row_order.csv": """id,name,age
1,Alice,30
2,Bob,25
3,Charlie,35
""",
    "file2_row_order.csv": """id,name,age
3,Charlie,35
1,Alice,30
2,Bob,25
""",
    "file1_column_order.csv": """id,name,age,city
1,Alice,30,Dublin
2,Bob,25,Cork
""",
    "file2_column_order.csv": """city,age,name,id
Dublin,30,Alice,1
Cork,25,Bob,2
""",
    "file1_ignore_column.csv": """id,name,age,updated_at
1,Alice,30,2024-01-01
2,Bob,25,2024-01-01
""",
    "file2_ignore_column.csv": """id,name,age,updated_at
1,Alice,30,2025-01-15
2,Bob,25,2025-01-15
""",
    "file1_no_headers.csv": """1,Alice,30,Dublin
2,Bob,25,Cork
""",
    "file2_no_headers.csv": """1,Alice,31,Dublin
2,Bob,25,Cork
""",
    "file1_real_world.csv": """user_id,email,plan,status,last_login
101,alice@test.com,free,active,2024-12-01
102,bob@test.com,pro,active,2024-12-05
103,charlie@test.com,free,inactive,2024-11-20
""",
    "file2_real_world.csv": """user_id,email,plan,status,last_login
101,alice@test.com,pro,active,2025-01-10
102,bob@test.com,pro,active,2025-01-08
104,diana@test.com,free,active,2025-01-02
""",
}


def main():
    output_dir = Path.cwd()
    print(f"Writing CSV files to: {output_dir}\n")

    for filename, content in FILES.items():
        path = output_dir / filename
        path.write_text(content.strip() + "\n", encoding="utf-8")
        print(f"✔ Created {filename}")

    print("\nAll test CSV files generated successfully 🎉")


if __name__ == "__main__":
    main()
