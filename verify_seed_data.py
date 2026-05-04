from pathlib import Path


def count_seed_rows(sql_path: Path) -> int:
    text = sql_path.read_text(encoding="utf-8")
    in_insert = False
    count = 0
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("INSERT INTO reviews"):
            in_insert = True
            continue
        if in_insert:
            if stripped.startswith("("):
                count += 1
            if stripped.endswith(";"):
                break
    return count


if __name__ == "__main__":
    sql_file = Path("db") / "init.sql"
    total = count_seed_rows(sql_file)
    print(f"Seeded rows found: {total}")
    if total != 50:
        raise SystemExit("Expected 50 seeded rows.")

