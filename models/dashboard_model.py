from database.db import conectar


def buscar_indicadores_dashboard():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS total_usuarios FROM usuarios")
    total_usuarios = cursor.fetchone()["total_usuarios"]

    cursor.execute("SELECT COUNT(*) AS total_acessos FROM acessos")
    total_acessos = cursor.fetchone()["total_acessos"]

    cursor.execute("SELECT COUNT(*) AS acessos_permitidos FROM acessos WHERE status = 'PERMITIDO'")
    acessos_permitidos = cursor.fetchone()["acessos_permitidos"]

    cursor.execute("""
        SELECT COUNT(*) AS acessos_hoje 
        FROM acessos 
        WHERE DATE(data_hora) = CURDATE()
    """)
    acessos_hoje = cursor.fetchone()["acessos_hoje"]

    cursor.execute("""
        SELECT u.nome, COUNT(a.id) AS total
        FROM acessos a
        INNER JOIN usuarios u ON u.id = a.usuario_id
        GROUP BY u.id, u.nome
        ORDER BY total DESC
        LIMIT 5
    """)
    top_usuarios = cursor.fetchall()

    cursor.execute("""
        SELECT DATE(data_hora) AS data, COUNT(*) AS total
        FROM acessos
        GROUP BY DATE(data_hora)
        ORDER BY data_hora DESC
        LIMIT 7
    """)
    acessos_por_dia = cursor.fetchall()

    cursor.close()
    conn.close()

    return {
        "total_usuarios": total_usuarios,
        "total_acessos": total_acessos,
        "acessos_permitidos": acessos_permitidos,
        "acessos_hoje": acessos_hoje,
        "top_usuarios": top_usuarios,
        "acessos_por_dia": acessos_por_dia
    }