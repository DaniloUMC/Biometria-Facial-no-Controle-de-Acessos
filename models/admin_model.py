from database.db import conectar


def buscar_admin_por_email(email):
    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM admins WHERE email = %s",
        (email,)
    )

    admin = cursor.fetchone()

    cursor.close()
    conn.close()

    return admin