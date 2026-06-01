def mascarar_cpf(cpf):
    if not cpf:
        return ""

    cpf_limpo = "".join(filter(str.isdigit, str(cpf)))

    if len(cpf_limpo) < 11:
        return "***" + cpf_limpo[-5:]

    return "***.***." + cpf_limpo[6:9] + "-" + cpf_limpo[9:11]


def mascarar_email(email):
    if not email:
        return ""

    partes = email.split("@")

    if len(partes) != 2:
        return email[:4] + "***"

    usuario = partes[0]
    dominio = partes[1]

    inicio = usuario[:4]

    return inicio + "***@" + dominio


def mascarar_usuario(usuario):
    usuario["cpf_mascarado"] = mascarar_cpf(usuario.get("cpf"))
    usuario["email_mascarado"] = mascarar_email(usuario.get("email"))

    return usuario


def mascarar_lista_usuarios(usuarios):
    return [mascarar_usuario(usuario) for usuario in usuarios]