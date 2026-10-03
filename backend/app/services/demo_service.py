import os
import json
import random
from typing import Dict, Any, List

class DemoService:
    def __init__(self):
        self.slow_queries = []
        self.explain_plans = {}
        self.base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

    def init_demo_data(self):
        try:
            db_path = os.path.join(self.base_path, "database")
            
            # Load slow queries
            sq_path = os.path.join(db_path, "slow_queries.sql")
            if os.path.exists(sq_path):
                with open(sq_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    self.slow_queries = [{"sql": q.strip() + ";"} for q in content.split(";") if q.strip()]

            # Load explain plans
            ep_path = os.path.join(db_path, "explain_plans.json")
            if os.path.exists(ep_path):
                with open(ep_path, "r", encoding="utf-8") as f:
                    self.explain_plans = json.load(f)
                    
        except Exception as e:
            print(f"Error loading demo data: {e}")
            self.slow_queries = [{"sql": "SELECT * FROM users WHERE age > 30;"}]
            self.explain_plans = {}

    def get_slow_queries(self) -> List[Dict[str, Any]]:
        # Try to get live queries from pg_stat_statements extension
        try:
            import sys, os
            sys.path.append(self.base_path)
            from database.connection import get_db_connection, release_db_connection
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('''
                SELECT query, calls, mean_exec_time 
                FROM pg_stat_statements 
                WHERE query NOT ILIKE '%pg_%' AND query NOT ILIKE '%COMMIT%' 
                ORDER BY mean_exec_time DESC 
                LIMIT 10
            ''')
            rows = cur.fetchall()
            release_db_connection(conn)
            if rows:
                return [{'sql': r[0], 'calls': r[1], 'mean_exec_time_ms': round(r[2], 2), 'source': 'pg_stat_statements (Live Extension)'} for r in rows]
        except Exception as e:
            print("Could not load from pg_stat_statements, falling back to static list. Error:", e)
        
        # Fallback to demo file
        return self.slow_queries

    def get_explain_plans(self) -> Dict[str, Any]:
        return self.explain_plans
        
    def get_synthetic_table_stats(self) -> Dict[str, Any]:
        return {
            "users": {"row_count": 1000000, "size_mb": 500},
            "orders": {"row_count": 5000000, "size_mb": 2000}
        }

demo_service = DemoService()

