// Configuration Socket.IO commune
const socket = io();

// Utilitaires communs
function getUrlParams() {
    return new URLSearchParams(window.location.search);
}

// Gestion des erreurs de connexion
socket.on('connect_error', (error) => {
    console.error('Erreur de connexion:', error);
});

socket.on('disconnect', (reason) => {
    console.log('Déconnecté:', reason);
});