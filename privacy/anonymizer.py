# pip install sqlglot pydantic
from pydantic import BaseModel
from typing import Dict, Any, List
import sqlglot
import sqlglot.expressions as exp

class AnonymizedResult(BaseModel):
    anonymized_sql: str
    table_mapping: Dict[str, str]
    column_mapping: Dict[str, str]
    literal_count: int
    anonymization_status: str

class SQLAnonymizer:
    def __init__(self):
        self.table_counter = 1
        self.column_counter = 1
        self.table_mapping: Dict[str, str] = {}
        self.column_mapping: Dict[str, str] = {}
        self.literal_count = 0

    def _get_table_alias(self, table_name: str) -> str:
        if table_name not in self.table_mapping:
            self.table_mapping[table_name] = f"TABLE_{self.table_counter}"
            self.table_counter += 1
        return self.table_mapping[table_name]

    def _get_column_alias(self, column_name: str) -> str:
        if column_name not in self.column_mapping:
            self.column_mapping[column_name] = f"COL_{self.column_counter}"
            self.column_counter += 1
        return self.column_mapping[column_name]

    def anonymize(self, sql: str) -> AnonymizedResult:
        self.table_mapping = {}
        self.column_mapping = {}
        self.literal_count = 0
        self.table_counter = 1
        self.column_counter = 1
        
        try:
            parsed = sqlglot.parse_one(sql)
            
            def transform_node(node):
                if isinstance(node, exp.Table):
                    table_name = node.name
                    if table_name:
                        node.set("this", exp.Identifier(this=self._get_table_alias(table_name)))
                elif isinstance(node, exp.Column):
                    col_name = node.name
                    if col_name:
                        node.set("this", exp.Identifier(this=self._get_column_alias(col_name)))
                    # table part
                    if node.args.get("table"):
                        table_part = node.args["table"].name
                        if table_part:
                            node.set("table", exp.Identifier(this=self._get_table_alias(table_part)))
                elif isinstance(node, exp.Literal):
                    self.literal_count += 1
                    node.set("this", "?")
                
                return node
                
            transformed = parsed.transform(transform_node)
            anonymized_sql = transformed.sql()
            status = "SUCCESS"
        except Exception as e:
            anonymized_sql = sql
            status = f"FAILED: {str(e)}"
            
        return AnonymizedResult(
            anonymized_sql=anonymized_sql,
            table_mapping=self.table_mapping,
            column_mapping=self.column_mapping,
            literal_count=self.literal_count,
            anonymization_status=status
        )
