const buscaRegistro = document.getElementById("buscaRegistro");
const statusRegistro = document.getElementById("statusRegistro");
const dataInicio = document.getElementById("dataInicio");
const dataFim = document.getElementById("dataFim");
const btnFiltrar = document.getElementById("btnFiltrarRegistros");
const btnExportar = document.getElementById("btnExportarRegistros");
const btnCarregarMais = document.getElementById("btnCarregarMaisRegistros");
const listaRegistros = document.getElementById("listaRegistros");

let offset = 50;

function parametros(offsetAtual = 0) {
    return new URLSearchParams({
        termo: buscaRegistro.value.trim(),
        status: statusRegistro.value,
        data_inicio: dataInicio.value,
        data_fim: dataFim.value,
        offset: offsetAtual
    });
}

function criarLinha(acesso) {
    return `
        <tr>
            <td>${acesso.id || ""}</td>
            <td>${acesso.usuario_registro || ""}</td>
            <td>${acesso.cpf || ""}</td>
            <td>${acesso.status || ""}</td>
            <td>${acesso.observacao || ""}</td>
            <td>${acesso.distancia ? Number(acesso.distancia).toFixed(4) : "0.0000"}</td>
            <td>${acesso.data_hora || ""}</td>
        </tr>
    `;
}

async function carregarRegistros(resetar = false) {
    if (resetar) {
        offset = 0;
        listaRegistros.innerHTML = "";
    }

    const response = await fetch(`/registros/listar?${parametros(offset).toString()}`);
    const registros = await response.json();

    registros.forEach(registro => {
        listaRegistros.innerHTML += criarLinha(registro);
    });

    offset += 50;

    btnCarregarMais.style.display = registros.length < 50 ? "none" : "inline-block";
}

btnFiltrar.addEventListener("click", function () {
    carregarRegistros(true);
});

btnCarregarMais.addEventListener("click", function () {
    carregarRegistros(false);
});

btnExportar.addEventListener("click", function () {
    const params = parametros(0);
    window.location.href = `/registros/exportar?${params.toString()}`;
});

buscaRegistro.addEventListener("keyup", function (e) {
    if (e.key === "Enter") {
        carregarRegistros(true);
    }
});