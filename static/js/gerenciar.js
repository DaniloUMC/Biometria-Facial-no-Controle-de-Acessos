const buscaInput = document.getElementById("buscaUsuario");
const btnBuscar = document.getElementById("btnBuscar");
const btnCarregarMais = document.getElementById("btnCarregarMais");
const listaUsuarios = document.getElementById("listaUsuarios");

let offset = 25;
let termoAtual = "";

function criarLinha(usuario) {
    return `
        <tr>
            <td>${usuario.nome || ""}</td>
            <td>${usuario.cpf_mascarado || ""}</td>
            <td>${usuario.email_mascarado || ""}</td>
            <td>${usuario.cidade || ""}</td>
            <td>${usuario.estado || ""}</td>
            <td>${usuario.data_cadastro || ""}</td>
            <td>
                <a href="/usuario/editar/${usuario.id}" class="btn btn-sm btn-warning">
                    Editar
                </a>

                <form method="POST" action="/usuario/excluir/${usuario.id}" style="display:inline;">
                    <button class="btn btn-sm btn-danger" onclick="return confirm('Deseja excluir este usuário?')">
                        Excluir
                    </button>
                </form>
            </td>
        </tr>
    `;
}

async function carregarUsuarios(resetar = false) {
    if (resetar) {
        offset = 0;
        listaUsuarios.innerHTML = "";
    }

    const response = await fetch(
        `/usuarios/listar?termo=${encodeURIComponent(termoAtual)}&offset=${offset}`
    );

    const usuarios = await response.json();

    usuarios.forEach(usuario => {
        listaUsuarios.innerHTML += criarLinha(usuario);
    });

    offset += 25;

    if (usuarios.length < 25) {
        btnCarregarMais.style.display = "none";
    } else {
        btnCarregarMais.style.display = "inline-block";
    }
}

btnBuscar.addEventListener("click", function () {
    termoAtual = buscaInput.value.trim();
    carregarUsuarios(true);
});

buscaInput.addEventListener("keyup", function (e) {
    if (e.key === "Enter") {
        termoAtual = buscaInput.value.trim();
        carregarUsuarios(true);
    }
});

btnCarregarMais.addEventListener("click", function () {
    carregarUsuarios(false);
});