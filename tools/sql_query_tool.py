
import sqlite3
from tools.base_tool import BaseTool
from typing import Dict, Any

class SQLQueryTool(BaseTool):
    def get_name(self) -> str:
        return "SQLQueryTool"

    def get_description(self) -> str:
        return "Executes read-only SQL queries against a SQLite database (payments/customers data)."

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The SQL query to execute. Must be a SELECT statement."
                }
            },
            "required": ["query"]
        }

    def execute(self, query: str) -> Dict[str, Any]:
        if not query.strip().lower().startswith("select"):
            return {"error": "Only SELECT queries are allowed.", "status": "failure"}

        conn = None
        try:
            conn = sqlite3.connect('./data/app.db')
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            return {"results": [dict(zip(columns, row)) for row in rows], "status": "success"}
        except sqlite3.Error as e:
            return {"error": f"Database error: {e}", "status": "failure"}
        finally:
            if conn:
                conn.close()
