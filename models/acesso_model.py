from database.db import conectar


def registrar_acesso(usuario_registro, cpf, status, observacao, distancia):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO acessos
        (usuario_registro, cpf, status, observacao, distancia)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        usuario_registro,
        cpf,
        status,
        observacao,
        distancia
    ))

    conn.commit()
    cursor.close()
    conn.close()

    return True


def listar_acessos(termo="", status="", data_inicio="", data_fim="", limite=50, offset=0):
    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT id, usuario_registro, cpf, status, observacao, distancia, data_hora
    FROM acessos
    WHERE 1=1
    """

    params = []

    if termo:
        query += " AND usuario_registro LIKE %s"
        params.append(f"%{termo}%")

    if status:
        query += " AND status = %s"
        params.append(status)

    if data_inicio:
        query += " AND DATE(data_hora) >= %s"
        params.append(data_inicio)

    if data_fim:
        query += " AND DATE(data_hora) <= %s"
        params.append(data_fim)

    query += " ORDER BY data_hora DESC LIMIT %s OFFSET %s"
    params.extend([limite, offset])

    cursor.execute(query, params)
    acessos = cursor.fetchall()

    cursor.close()
    conn.close()

    return acessos