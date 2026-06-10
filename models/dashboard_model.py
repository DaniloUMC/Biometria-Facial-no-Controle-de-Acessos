from database.db import conectar


def buscar_indicadores_dashboard():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT COUNT(*) AS total_acessos
        FROM acessos
    """)
    total_acessos = cursor.fetchone()["total_acessos"]

    cursor.execute("""
        SELECT COUNT(*) AS acessos_permitidos
        FROM acessos
        WHERE status = 'PERMITIDO'
    """)
    acessos_permitidos = cursor.fetchone()["acessos_permitidos"]

    cursor.execute("""
        SELECT COUNT(*) AS acessos_negados
        FROM acessos
        WHERE status <> 'PERMITIDO'
    """)
    acessos_negados = cursor.fetchone()["acessos_negados"]

    cursor.execute("""
        SELECT COUNT(*) AS acessos_hoje
        FROM acessos
        WHERE DATE(data_hora) = CURDATE()
    """)
    acessos_hoje = cursor.fetchone()["acessos_hoje"]

    cursor.execute("""
        SELECT 
            usuario_registro AS nome,
            COUNT(id) AS total
        FROM acessos
        WHERE usuario_registro IS NOT NULL
        GROUP BY usuario_registro
        ORDER BY total DESC
        LIMIT 5
    """)
    top_usuarios = cursor.fetchall()

    cursor.execute("""
        SELECT 
            DATE(data_hora) AS data,
            COUNT(id) AS total
        FROM acessos
        GROUP BY DATE(data_hora)
        ORDER BY data ASC
        LIMIT 7
    """)
    acessos_por_dia = cursor.fetchall()

    cursor.execute("""
        SELECT
            id,
            usuario_registro,
            cpf,
            status,
            observacao,
            distancia,
            data_hora
        FROM acessos
        ORDER BY data_hora DESC
        LIMIT 10
    """)
    ultimos_acessos = cursor.fetchall()

    cursor.close()
    conn.close()

    return {
        "total_acessos": total_acessos,
        "acessos_permitidos": acessos_permitidos,
        "acessos_negados": acessos_negados,
        "acessos_hoje": acessos_hoje,
        "top_usuarios": top_usuarios,
        "acessos_por_dia": acessos_por_dia,
        "ultimos_acessos": ultimos_acessos
    }