// Gestion du lobby principal
let pseudo = "";

function showMenu() {
    document.getElementById('menu').style.display = '';
    document.getElementById('create').style.display = 'none';
    document.getElementById('join').style.display = 'none';
}

function showCreate() {
    document.getElementById('menu').style.display = 'none';
    document.getElementById('create').style.display = '';
    document.getElementById('join').style.display = 'none';
}

function showJoin() {
    document.getElementById('menu').style.display = 'none';
    document.getElementById('create').style.display = 'none';
    document.getElementById('join').style.display = '';
}

function createRoom() {
    pseudo = document.getElementById('pseudo').value.trim();
    const code = document.getElementById('create_code').value.trim().toUpperCase() || Math.random().toString(36).substr(2,6).toUpperCase();
    const visible = document.getElementById('create_visible').checked;
    if (!pseudo) { alert("Entrez un pseudo !"); return; }
    socket.emit('create_room', {code: code, pseudo: pseudo, visible: visible});
}

function joinRoom() {
    pseudo = document.getElementById('pseudo').value.trim();
    const code = document.getElementById('join_code').value.trim().toUpperCase();
    if (!pseudo) { alert("Entrez un pseudo !"); return; }
    socket.emit('join_room', {code: code, pseudo: pseudo});
}

function joinQueue() {
    pseudo = document.getElementById('pseudo').value.trim();
    if (!pseudo) {
        alert("Veuillez entrer un pseudo !");
        return;
    }
    socket.emit('join_queue', {pseudo: pseudo});
}

function showVisibleRooms() {
    socket.emit('get_visible_rooms');
}

// Événements Socket.IO pour le lobby
socket.on('room_created', data => {
    window.location.href = `/waiting?code=${data.code}&pseudo=${encodeURIComponent(pseudo)}`;
});

socket.on('room_joined', data => {
    window.location.href = `/waiting?code=${data.code}&pseudo=${encodeURIComponent(pseudo)}`;
});

socket.on('join_failed', data => {
    document.getElementById('join_error').innerText = data.reason;
});

socket.on('queue_joined', data => {
    alert("Vous êtes dans la file d'attente depuis " + data.date);
});

socket.on('visible_rooms', rooms => {
    const div = document.getElementById('visible_rooms');
    div.innerHTML = '';
    if (rooms.length === 0) {
        div.innerHTML = "<i>Aucun salon visible disponible.</i>";
    } else {
        rooms.forEach(room => {
            const btn = document.createElement('button');
            btn.textContent = `Salon ${room.code} (${room.players.length}/2)`;
            btn.onclick = () => {
                pseudo = document.getElementById('pseudo').value.trim();
                socket.emit('join_room', {code: room.code, pseudo: pseudo});
            };
            div.appendChild(btn);
        });
    }
});

// Vérification de l'état de connexion
fetch('/profile')
    .then(resp => {
        if (resp.redirected) {
            document.getElementById('login_prompt').style.display = '';
            document.getElementById('menu').style.display = 'none';
        } else {
            document.getElementById('login_prompt').style.display = 'none';
            document.getElementById('menu').style.display = '';
        }
    });

// Initialisation
showMenu();