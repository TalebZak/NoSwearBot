from psycopg2 import connect, sql
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
        self.cursor.execute(query, params)
        self.db.commit()

    def exist_and(self, table, fields, values):
        query = sql.SQL("SELECT * FROM {table} WHERE {condition}").format(
            table=sql.Identifier(table),
            condition=sql.SQL(" AND ").join(
                sql.Composed(sql.Identifier(field) + sql.SQL(' = ') + sql.Placeholder() for field in fields))
        )
        print(query.as_string(self.cursor))
        self.execute(query, values)
        return self.cursor.fetchone() is not None

    def insert(self, table, values):
        query = sql.SQL("INSERT INTO {table} VALUES ({placeholder})").format(
            table=sql.Identifier(table),
            placeholder=sql.SQL(', ').join([sql.Placeholder()] * len(values))
        )
        print(query.as_string(self.cursor))
        self.execute(query, values)

    def delete(self, table, conditions, values):
        query = sql.SQL("DELETE FROM {table} WHERE{conditions}").format(
            table=sql.Identifier(table),
            conditions=sql.SQL(" AND ").join(
                sql.Composed(sql.Identifier(conditions) + sql.SQL(' = ') + sql.Placeholder()
                             for conditions in conditions)
            )
        )
        print(query.as_string(self.cursor))
        self.execute(query, values)

    def set(self, table, fields, conditions, old_values, new_values):
        query = sql.SQL("UPDATE {table} SET {fields} WHERE {conditions}").format(
            table=sql.Identifier(table),
            fields=sql.SQL(" , ").join(
                sql.Composed(sql.Identifier(fields) + sql.SQL(' = ') + sql.Placeholder() for field in fields)),
            conditions=sql.SQL(" AND ").join(
                sql.Composed(sql.Identifier(conditions) + sql.SQL(' = ') + sql.Placeholder()
                             for conditions in conditions)
            )
        )
        print(query.as_string(self.cursor))
        self.execute(query, new_values+old_values)

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
        print(query.as_string(self.cursor))
        self.execute(query, values)
        return self.cursor.fetchall()



