#сохраняет в формате для БД

import psycopg2
from psycopg2.extras import execute_batch, DictCursor
from psycopg2 import sql
from typing import List, Dict, Any, Optional

def save_data_to_db_api(
    data: List[Dict[str, Any]],
    table_name: str,
    dbname: str,
    user: str,
    password: str,
    host: str,
    port: str = "5432",
    create_table: bool = True
) -> int:
    if not data:
        raise ValueError("No data to save")

    conn = psycopg2.connect(
        dbname=dbname,  # <-- важно
        user=user,
        password=password,
        host=host,
        port=port
    )

    try:
        cursor = conn.cursor(cursor_factory=DictCursor)

        columns = list(data[0].keys())
        columns_sql = sql.SQL(", ").join(sql.Identifier(c) for c in columns)
        values_sql = sql.SQL(", ").join(sql.Placeholder(c) for c in columns)

        if create_table:
            # базовая таблица + колонки
            cursor.execute(
                sql.SQL("CREATE TABLE IF NOT EXISTS {t} (id SERIAL PRIMARY KEY);")
                .format(t=sql.Identifier(table_name))
            )
            for c in columns:
                cursor.execute(
                    sql.SQL('ALTER TABLE {t} ADD COLUMN IF NOT EXISTS {c} VARCHAR(200);')
                    .format(t=sql.Identifier(table_name), c=sql.Identifier(c))
                )
            conn.commit()

        insert_q = sql.SQL("INSERT INTO {t} ({cols}) VALUES ({vals})").format(
            t=sql.Identifier(table_name),
            cols=columns_sql,
            vals=values_sql
        )

        execute_batch(cursor, insert_q, data)
        conn.commit()
        return len(data)

    finally:
        try:
            cursor.close()
        except:
            pass
        conn.close()