import json
import psycopg2
from app.config import DATABASE_URL


def get_connection():
    return psycopg2.connect(DATABASE_URL)


def init_db():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS historial (
                id SERIAL PRIMARY KEY,
                fecha TIMESTAMP DEFAULT NOW(),
                producto TEXT NOT NULL,
                plataformas TEXT[],
                precios JSONB,
                reporte TEXT
            )
        """)
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"PostgreSQL no disponible: {e}")


def save_analysis(producto: str, plataformas: list, precios: list, reporte: str):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO historial (producto, plataformas, precios, reporte) VALUES (%s, %s, %s, %s)",
            (producto, plataformas, json.dumps(precios), reporte)
        )
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"No se pudo guardar en PostgreSQL: {e}")


def get_history(producto: str = None, limit: int = 50):
    try:
        conn = get_connection()
        cur = conn.cursor()
        if producto:
            cur.execute(
                "SELECT fecha, producto, plataformas, precios, reporte FROM historial WHERE producto = %s ORDER BY fecha DESC LIMIT %s",
                (producto, limit)
            )
        else:
            cur.execute(
                "SELECT fecha, producto, plataformas, precios, reporte FROM historial ORDER BY fecha DESC LIMIT %s",
                (limit,)
            )
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [
            {
                "fecha": r[0].isoformat() if r[0] else None,
                "producto": r[1],
                "plataformas": r[2],
                "precios": r[3],
                "reporte": r[4],
            }
            for r in rows
        ]
    except Exception as e:
        return [{"error": str(e)}]
