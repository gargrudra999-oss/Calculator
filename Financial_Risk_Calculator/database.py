"""
SQLite3 Database Manager for storing and managing calculation history.

Automatically creates the local database file and schema on startup
using only Python's built-in sqlite3, datetime, and os modules.
"""

import datetime
import os
import sqlite3


class DatabaseError(Exception):
    """Raised when a local SQLite database operation fails."""


class DatabaseManager:
    """Manages local SQLite persistence for Financial Risk Calculator history."""

    DEFAULT_DB_NAME = "financial_risk_calculator.db"

    def __init__(self, db_path=None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            self.db_path = os.path.join(base_dir, self.DEFAULT_DB_NAME)
        else:
            self.db_path = os.path.abspath(db_path)

        parent_dir = os.path.dirname(self.db_path)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)

        self._initialize_database()

    def _run_in_connection(self, operation, error_message):
        """Open a SQLite connection, run operation(conn) transactionally, and close it."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            with conn:
                return operation(conn)
        except (sqlite3.Error, ValueError) as exc:
            raise DatabaseError(f"{error_message}: {exc}") from exc
        finally:
            if conn is not None:
                conn.close()

    def _initialize_database(self):
        """Create the calculation_history table if it does not already exist."""
        def _create_schema(conn):
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS calculation_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    input_details TEXT NOT NULL,
                    results TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )

        self._run_in_connection(_create_schema, "Failed to initialize database")

    def add_record(self, category, input_details, results):
        """Insert a completed calculation into history and return its record ID."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        def _insert(conn):
            cursor = conn.execute(
                """
                INSERT INTO calculation_history (
                    category, input_details, results, created_at
                ) VALUES (?, ?, ?, ?)
                """,
                (category, input_details, results, timestamp),
            )
            return cursor.lastrowid

        return self._run_in_connection(_insert, "Failed to save calculation history")

    def get_all_records(self, category_filter=None):
        """Return saved calculation records ordered from newest to oldest."""
        def _fetch(conn):
            if category_filter and category_filter != "All":
                rows = conn.execute(
                    """
                    SELECT id, category, input_details, results, created_at
                    FROM calculation_history
                    WHERE category = ?
                    ORDER BY id DESC
                    """,
                    (category_filter,),
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT id, category, input_details, results, created_at
                    FROM calculation_history
                    ORDER BY id DESC
                    """
                ).fetchall()
            return [dict(row) for row in rows]

        return self._run_in_connection(_fetch, "Failed to read calculation history")

    def delete_record(self, record_id):
        """Delete a single calculation record by its ID. Returns True if deleted."""
        def _delete(conn):
            cursor = conn.execute(
                "DELETE FROM calculation_history WHERE id = ?",
                (int(record_id),),
            )
            return cursor.rowcount > 0

        return self._run_in_connection(_delete, "Failed to delete history record")

    def clear_all_records(self):
        """Delete all records from calculation_history. Returns number deleted."""
        def _clear(conn):
            cursor = conn.execute("DELETE FROM calculation_history")
            return cursor.rowcount

        return self._run_in_connection(_clear, "Failed to clear calculation history")

    def get_summary_stats(self):
        """Return total count, latest record metadata, and per-category counts."""
        def _stats(conn):
            total_row = conn.execute(
                "SELECT COUNT(*) AS total FROM calculation_history"
            ).fetchone()
            latest_row = conn.execute(
                """
                SELECT id, category, results, created_at
                FROM calculation_history
                ORDER BY id DESC
                LIMIT 1
                """
            ).fetchone()
            cat_rows = conn.execute(
                """
                SELECT category, COUNT(*) AS count
                FROM calculation_history
                GROUP BY category
                """
            ).fetchall()

            return {
                "total": total_row["total"] if total_row else 0,
                "latest": dict(latest_row) if latest_row else None,
                "by_category": {row["category"]: row["count"] for row in cat_rows},
            }

        return self._run_in_connection(_stats, "Failed to query summary statistics")
