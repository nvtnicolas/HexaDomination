// Gestion de la salle d'attente
const params = getUrlParams();
const code = params.get('code');
const pseudo = params.get('pseudo');
let ready = false;

// Initialisation
document.getElementById('room_code').innerText = code;

// Rejoindre la room d'attente
socket.emit('waiting_room', {code: code, pseudo: pseudo});

// Affichage des joueurs et statut
socket.on('waiting_status', data => {
    let html = `<b>Joueurs (${data.players.length}/2):</b><ul>`;
    data.players.forEach(p => {
        html += `<li>${p.pseudo} ${p.ready ? '(Prêt)' : '(En attente)'}</li>`;
    });
    html += '</ul>';
    document.getElementById('players').innerHTML = html;
    document.getElementById('ready-btn').disabled = data.players.length < 2 || data.players.find(p => p.pseudo === pseudo && p.ready);
    document.getElementById('ready-status').innerText = data.players.length < 2 ? "En attente d'un autre joueur..." : "";
});

// Chat
function sendMsg() {
    const msg = document.getElementById('msg').value.trim();
    if (msg) {
        socket.emit('waiting_chat', {code: code, pseudo: pseudo, msg: msg});
        document.getElementById('msg').value = '';
    }
}

socket.on('waiting_chat', data => {
    const div = document.getElementById('messages');
    div.innerHTML += `<div><b>${data.pseudo}:</b> ${data.msg}</div>`;
    div.scrollTop = div.scrollHeight;
});

// Prêt
function setReady() {
    socket.emit('waiting_ready', {code: code, pseudo: pseudo});
}

// Lancement du jeu
socket.on('start_game', () => {
    window.location.href = `/game?code=${code}&pseudo=${encodeURIComponent(pseudo)}`;
});

// Event listener pour l'entrée
document.getElementById('msg').addEventListener('keydown', function(e) {
    if (e.key === 'Enter') {
        sendMsg();
    }
});