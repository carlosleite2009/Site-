// ======================================================
// SISTEMA DE REGISTRO DE SOLICITAÇÕES
// Equipe 5 - JavaScript e Integração
// Mantém os IDs e os fluxos das telas HTML existentes.
// ======================================================

// Se o backend estiver em outro endereço, altere esta constante.
// Em produção, use a URL pública do backend (não a URL do GitHub Pages).
const API_BASE_URL = window.API_BASE_URL || "http://127.0.0.1:5000";

const API = {
    cadastro: `${API_BASE_URL}/cadastro`,
    login: `${API_BASE_URL}/login`,
    solicitacoes: `${API_BASE_URL}/solicitacoes`
};

// ------------------------------------------------------
// Comunicação centralizada com a API
// ------------------------------------------------------
async function enviarParaAPI(endereco, dados = null, metodo = "POST") {
    try {
        const opcoes = {
            method: metodo,
            headers: { "Accept": "application/json" },
            credentials: "include"
        };

        if (dados !== null) {
            opcoes.headers["Content-Type"] = "application/json";
            opcoes.body = JSON.stringify(dados);
        }

        const resposta = await fetch(endereco, opcoes);
        const texto = await resposta.text();
        let resultado = {};

        if (texto) {
            try {
                resultado = JSON.parse(texto);
            } catch {
                throw new Error("O servidor retornou uma resposta inválida.");
            }
        }

        if (!resposta.ok) {
            throw new Error(
                resultado.erro ||
                resultado.mensagem ||
                `Erro na operação (HTTP ${resposta.status}).`
            );
        }

        return resultado;
    } catch (erro) {
        console.error("Erro na comunicação com a API:", erro);
        alert(
            erro.message.includes("Failed to fetch") || erro instanceof TypeError
                ? "Não foi possível conectar ao servidor. Verifique se a API Python está ligada e se o endereço está correto."
                : erro.message
        );
        return null;
    }
}

// ------------------------------------------------------
// Cadastro
// IDs esperados: cadastroForm, nome, email, usuario,
// senha e confirmar.
// ------------------------------------------------------
const cadastroForm = document.getElementById("cadastroForm");

if (cadastroForm) {
    cadastroForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        const nome = document.getElementById("nome")?.value.trim();
        const email = document.getElementById("email")?.value.trim();
        const usuario = document.getElementById("usuario")?.value.trim();
        const senha = document.getElementById("senha")?.value;
        const confirmar = document.getElementById("confirmar")?.value;

        if (!nome || !email || !usuario || !senha || !confirmar) {
            alert("Preencha todos os campos!");
            return;
        }

        if (senha !== confirmar) {
            alert("As senhas não são iguais!");
            return;
        }

        // O backend precisa receber também o campo "login".
        const resultado = await enviarParaAPI(API.cadastro, {
            nome,
            email,
            login: usuario,
            senha
        });

        if (resultado) {
            alert(resultado.mensagem || "Usuário cadastrado com sucesso!");
            cadastroForm.reset();
            // Mantém o fluxo original: volta para a tela inicial/login.
            window.location.href = "index2.html";
        }
    });
}

// ------------------------------------------------------
// Login
// IDs esperados: loginForm, usuario e senha.
// ------------------------------------------------------
const loginForm = document.getElementById("loginForm");

if (loginForm) {
    loginForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        const usuario = document.getElementById("usuario")?.value.trim();
        const senha = document.getElementById("senha")?.value;

        if (!usuario || !senha) {
            alert("Preencha o login e a senha!");
            return;
        }

        const resultado = await enviarParaAPI(API.login, {
            login: usuario,
            senha
        });

        if (resultado) {
            alert(resultado.mensagem || "Login realizado com sucesso!");

            // Mantém compatibilidade com a interface já existente.
            if (resultado.nome != null) {
                sessionStorage.setItem("usuarioNome", resultado.nome);
            }
            if (resultado.id != null) {
                sessionStorage.setItem("usuarioId", String(resultado.id));
            }

            window.location.href = "painel.html";
        }
    });
}

// ------------------------------------------------------
// Solicitações
// Estas funções podem ser chamadas pelo painel.html.
// ------------------------------------------------------
async function registrarSolicitacao(nome, titulo, descricao) {
    if (!nome || !titulo || !descricao) {
        alert("Preencha o nome, o título e a descrição da solicitação.");
        return null;
    }

    return await enviarParaAPI(API.solicitacoes, {
        nome,
        titulo,
        descricao
    });
}

async function listarSolicitacoes() {
    try {
        const resposta = await fetch(API.solicitacoes, {
            method: "GET",
            headers: { "Accept": "application/json" },
            credentials: "include"
        });

        const texto = await resposta.text();
        let resultado = texto ? JSON.parse(texto) : [];

        if (!resposta.ok) {
            throw new Error(
                resultado.erro ||
                resultado.mensagem ||
                "Erro ao listar solicitações."
            );
        }

        return resultado;
    } catch (erro) {
        console.error("Erro ao listar solicitações:", erro);
        alert("Não foi possível carregar as solicitações. Verifique o servidor.");
        return null;
    }
}

async function atualizarStatus(id, status) {
    if (id == null || !status) {
        alert("Informe o identificador e o novo status.");
        return null;
    }

    return await enviarParaAPI(
        `${API.solicitacoes}/${encodeURIComponent(id)}`,
        { status },
        "PUT"
    );
}

async function excluirSolicitacao(id) {
    if (id == null) {
        alert("Solicitação inválida.");
        return null;
    }

    return await enviarParaAPI(
        `${API.solicitacoes}/${encodeURIComponent(id)}`,
        null,
        "DELETE"
    );
}

// ------------------------------------------------------
// Logout opcional para o painel, caso exista botão com
// id="logoutBtn". Requer rota POST /logout no backend.
// ------------------------------------------------------
const logoutBtn = document.getElementById("logoutBtn");

if (logoutBtn) {
    logoutBtn.addEventListener("click", async () => {
        const resultado = await enviarParaAPI(`${API_BASE_URL}/logout`, {});
        if (resultado) {
            sessionStorage.removeItem("usuarioNome");
            sessionStorage.removeItem("usuarioId");
            window.location.href = "index2.html";
        }
    });
}
