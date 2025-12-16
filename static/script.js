let topicos = [];
let filtroAtual = "pendentes";
let todosAbertos = false;


/* ===============================
   CARGA INICIAL (única)
================================ */

window.onload = async () => {
    const res = await fetch("/dados")
    const dados = await res.json();

    topicos = dados.map(t => ({
        ...t,
        aberto: false
    }));

    renderizar();
};

function exportarRelatorio() {
    window.location.href = "/exportar";
}


/* ===============================
   TÓPICOS
================================ */

async function adicionarTopico() {
    const input = document.getElementById("novoTopico");
    const nome = input.value.trim();
    if (!nome) return;

    const res = await fetch("http://127.0.0.1:5000/topico", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ nome })
    });

    const novoTopico = await res.json();

    topicos.push({
        ...novoTopico,
        aberto: true
    });

    input.value = "";
    renderizar();
}

function toggleTopico(i) {
    topicos[i].aberto = !topicos[i].aberto;
    renderizar();
}

function toggleTodos() {
    todosAbertos = !todosAbertos;
    topicos.forEach(t => t.aberto = todosAbertos);

    document.getElementById("btnExpandir").innerText =
        todosAbertos ? "Recolher tudo" : "Expandir tudo";

    renderizar();
}


/* ===============================
   TAREFAS
================================ */

async function adicionarTarefa(i, urgencia) {
    const input = document.getElementById(`tarefa-${i}`);
    const texto = input.value.trim();
    if (!texto) return;

    const res = await fetch("http://127.0.0.1:5000/tarefa", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            topico_id: topicos[i].id,
            texto,
            urgencia
        })
    });

    const tarefa = await res.json();
    topicos[i].tarefas.push(tarefa);

    input.value = "";
    renderizar();
}

async function concluirTarefa(tarefaId, topicoIndex) {
    await fetch("http://127.0.0.1:5000/concluir", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ tarefa_id: tarefaId })
    });

    const tarefa = topicos[topicoIndex].tarefas.find(t => t.id === tarefaId);
    if (tarefa) tarefa.concluida = true;

    renderizar();
}


/* ===============================
   FILTROS
================================ */

function setFiltro(tipo) {
    filtroAtual = tipo;

    document.getElementById("btnPendentes")
        .classList.toggle("ativo", tipo === "pendentes");

    document.getElementById("btnConcluidas")
        .classList.toggle("ativo", tipo === "concluidas");

    renderizar();
}

function filtrarTopicos() {
    const termo = document.getElementById("pesquisa").value.toLowerCase();
    document.querySelectorAll(".card").forEach(card => {
        card.style.display = card.innerText.toLowerCase().includes(termo)
            ? "block"
            : "none";
    });
}


/* ===============================
   RENDERIZAÇÃO
================================ */

function renderizar() {
    const container = document.getElementById("listaTopicos");
    container.innerHTML = "";

    topicos.forEach((topico, i) => {
        const card = document.createElement("div");
        card.className = "card";

        const tarefas = topico.tarefas
            .filter(t =>
                filtroAtual === "pendentes" ? !t.concluida : t.concluida
            )
            .sort((a, b) => {
                const ordem = { alta: 1, media: 2, baixa: 3 };
                return ordem[a.urgencia] - ordem[b.urgencia];
            });

        card.innerHTML = `
            <h3 onclick="toggleTopico(${i})">${topico.nome}</h3>

            ${topico.aberto ? `
                <div class="lista-tarefas">
                    ${tarefas.map(t => `
                        <div class="tarefa urg-${t.urgencia}">
                            <span>${t.texto}</span>
                            ${!t.concluida
                                ? `<button type="button" onclick="concluirTarefa(${t.id}, ${i})">Concluir</button>
`
                                : ""
                            }
                        </div>
                    `).join("")}
                </div>

                <div class="form-tarefa">
                    <input id="tarefa-${i}" placeholder="Nova descrição">
                    <div class="urgencias">
                        <button type="button" class="btn-alta"
                                onclick="adicionarTarefa(${i}, 'alta')">Alta</button>

                        <button type="button" class="btn-media"
                                onclick="adicionarTarefa(${i}, 'media')">Média</button>

                        <button type="button" class="btn-baixa"
                                onclick="adicionarTarefa(${i}, 'baixa')">Baixa</button>                    </div>
                </div>
            ` : ""}
        `;
        container.appendChild(card);
    });
}

window.addEventListener("beforeunload", () => {
    console.log("🚨 RELOAD DETECTADO");
});

