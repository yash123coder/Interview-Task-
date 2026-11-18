import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path("data/leads.db")


def migrate():
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Database not found: {DB_PATH}"
        )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = DB_PATH.with_name(
        f"leads_backup_{timestamp}.db"
    )

    with sqlite3.connect(DB_PATH) as source:
        with sqlite3.connect(backup_path) as backup:
            source.backup(backup)

        columns = {
            row[1]
            for row in source.execute(
                "PRAGMA table_info(lead_analysis)"
            ).fetchall()
        }

        if not columns:
            raise RuntimeError(
                "lead_analysis table does not exist."
            )

        migrations = {
            "reasoning": "ALTER TABLE lead_analysis ADD COLUMN reasoning TEXT",
            "recommended_action": (
                "ALTER TABLE lead_analysis "
                "ADD COLUMN recommended_action TEXT"
            ),
            "missing_information": (
                "ALTER TABLE lead_analysis "
                "ADD COLUMN missing_information JSON"
            ),
        }

        for column, sql in migrations.items():
            if column not in columns:
                source.execute(sql)
                print(f"Added column: {column}")
            else:
                print(f"Column already exists: {column}")

        source.commit()

    print("\nDatabase migration completed.")
    print(f"Backup created: {backup_path}")


if __name__ == "__main__":
    migrate()