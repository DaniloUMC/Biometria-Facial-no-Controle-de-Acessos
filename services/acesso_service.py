from models.acesso_model import listar_acessos


def obter_registros(termo="", status="", data_inicio="", data_fim="", limite=50, offset=0):
    return listar_acessos(termo, status, data_inicio, data_fim, limite, offset)