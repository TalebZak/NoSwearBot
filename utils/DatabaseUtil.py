from psycopg2 import connect, sql, errors
from dotenv import load_dotenv
from os import getenv

load_dotenv()


class DatabaseUtil:
    def __init__(self):
        ENDPOINT = getenv('ENDPOINT')
        PORT = 5432
        USR = getenv('USR')
        PASS = getenv('PASS')
        DBNAME = getenv('DBNAME')
        self.db = connect(
            host=ENDPOINT,
            port=PORT,
            user=USR,
            password=PASS,
            dbname=DBNAME
        )
        self.cursor = self.db.cursor()
        self.cursor.execute(open("TableCreate.sql", "r").read())
        self.db.commit()

    def execute(self, query, params):
        try:
            self.cursor.execute(query, params)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise e

    def exist_and(self, table, fields, values):
        query = sql.SQL("SELECT * FROM {table} WHERE {condition}").format(
            table=sql.Identifier(table),
            condition=sql.SQL(" AND ").join(
                sql.Composed(sql.Identifier(field) + sql.SQL(' = ') + sql.Placeholder() for field in fields))
        )
        self.execute(query, values)
        return self.cursor.fetchone() is not None

    def insert(self, table, values):
        query = sql.SQL("INSERT INTO {table} VALUES ({placeholder})").format(
            table=sql.Identifier(table),
            placeholder=sql.SQL(', ').join([sql.Placeholder()] * len(values))
        )
        try:
            self.execute(query, values)
        except Exception as e:
            raise e

    def delete(self, table, conditions, values):
        query = sql.SQL("DELETE FROM {table} WHERE{conditions}").format(
            table=sql.Identifier(table),
            conditions=sql.SQL(" AND ").join(
                sql.Composed(sql.Identifier(condition) + sql.SQL(' = ') + sql.Placeholder()
                             for condition in conditions)
            )
        )
        self.execute(query, values)

    def set(self, table, fields, conditions, new_values, conditions_values):
        query = sql.SQL("UPDATE {table} SET {fields} WHERE {conditions}").format(
            table=sql.Identifier(table),
            fields=sql.SQL(" , ").join(
                sql.Composed(sql.Identifier(field) + sql.SQL(' = ') + sql.Placeholder() for field in fields)),
            conditions=sql.SQL(" AND ").join(
                sql.Composed(sql.Identifier(condition) + sql.SQL(' = ') + sql.Placeholder()
                             for condition in conditions)
            )
        )
        self.execute(query, new_values + conditions_values)

    def get(self, table, fields=None, conditions=None, values=None):
        if values is None:
            values = []
        if not fields:
            fields = ()
        if not conditions:
            conditions = ()
        query = sql.SQL("SELECT {fields} FROM {table} WHERE {conditions}").format(
            fields=sql.SQL(" , ").join(
                sql.Composed(sql.Identifier(field) for field in fields)),
            table=sql.Identifier(table),
            conditions=sql.SQL(" AND ").join(
                sql.Composed(sql.Identifier(conditions) + sql.SQL(' = ') + sql.Placeholder()
                             for conditions in conditions)
            )
        )
        self.execute(query, values)
        return self.cursor.fetchall()
