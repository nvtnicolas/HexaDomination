// Variables de jeu
let towers = [];
const rows = 6, cols = 8;
const tileW = 60, tileH = 30;
let money = 100;
let lives = 20;
let enemies = [];
let wave = 1;
let waveEnemies = 5;
let waveHp = 2;
let waveActive = false;
let waveTimeout = null;
let selectedTower = null;

// Chemin des ennemis
const path = [
    {i: 0, j: 0}, {i: 0, j: 1}, {i: 0, j: 2}, {i: 1, j: 2}, {i: 2, j: 2},
    {i: 2, j: 3}, {i: 2, j: 4}, {i: 3, j: 4}, {i: 4, j: 4}, {i: 5, j: 4}, 
    {i: 5, j: 5}, {i: 5, j: 6}, {i: 5, j: 7}
];

// Caractéristiques des tours
const towerLevels = [
    {name: "Triangle", price: 30, range: 1.5, color: "#3a6", shape: "triangle", upgrade: 40},
    {name: "Carré", price: 40, range: 2, color: "#36a", shape: "square", upgrade: 60},
    {name: "Pentagone", price: 60, range: 2.5, color: "#a63", shape: "pentagon", upgrade: 90},
    {name: "Hexagone", price: 90, range: 3, color: "#a36", shape: "hexagon", upgrade: null}
];

// Fonctions utilitaires
function isoX(i, j) { return 80 + j * tileW + i * tileW/2; }
function isoY(i, j) { return 60 + i * tileH; }

function drawBoard() {
    const ctx = document.getElementById('board').getContext('2d');
    ctx.clearRect(0,0,700,400);
    
    // Grille
    for(let i=0;i<rows;i++) for(let j=0;j<cols;j++) {
        let x = isoX(i,j), y = isoY(i,j);
        ctx.beginPath();
        ctx.moveTo(x, y);
        ctx.lineTo(x+tileW/2, y+tileH/2);
        ctx.lineTo(x, y+tileH);
        ctx.lineTo(x-tileW/2, y+tileH/2);
        ctx.closePath();
        ctx.strokeStyle = "#888";
        ctx.stroke();
    }
    
    // Chemin
    for(const cell of path) {
        let x = isoX(cell.i, cell.j), y = isoY(cell.i, cell.j);
        ctx.fillStyle = "#ffe066";
        ctx.beginPath();
        ctx.moveTo(x, y);
        ctx.lineTo(x+tileW/2, y+tileH/2);
        ctx.lineTo(x, y+tileH);
        ctx.lineTo(x-tileW/2, y+tileH/2);
        ctx.closePath();
        ctx.fill();
    }
    
    // Tours
    for(const t of towers) {
        let x = isoX(t.i, t.j), y = isoY(t.i, t.j);
        ctx.save();
        ctx.translate(x, y+tileH/2);
        
        if(selectedTower && selectedTower.i === t.i && selectedTower.j === t.j) {
            ctx.beginPath();
            ctx.arc(0, 0, towerLevels[t.level-1].range*tileW, 0, 2*Math.PI);
            ctx.strokeStyle = "#0c0";
            ctx.globalAlpha = 0.2;
            ctx.fillStyle = "#0c0";
            ctx.fill();
            ctx.globalAlpha = 1;
            ctx.stroke();
        }
        
        drawTowerShape(ctx, t.level);
        ctx.restore();
    }
    
    // Ennemis
    for(const e of enemies) {
        let pos = path[Math.floor(e.progress)];
        if(!pos) continue;
        let next = path[Math.floor(e.progress)+1] || pos;
        let frac = e.progress - Math.floor(e.progress);
        let i = pos.i + (next.i-pos.i)*frac;
        let j = pos.j + (next.j-pos.j)*frac;
        let x = isoX(i,j), y = isoY(i,j);
        
        ctx.beginPath();
        ctx.arc(x, y+tileH/2, 13, 0, 2*Math.PI);
        ctx.fillStyle = "#c33";
        ctx.fill();
        ctx.strokeStyle = "#222";
        ctx.stroke();
        
        ctx.fillStyle = "#222";
        ctx.fillRect(x-14, y+tileH/2-20, 28, 5);
        ctx.fillStyle = "#0c0";
        ctx.fillRect(x-14, y+tileH/2-20, 28*(e.hp/e.maxHp), 5);
        ctx.strokeStyle = "#000";
        ctx.strokeRect(x-14, y+tileH/2-20, 28, 5);
    }
}

function drawTowerShape(ctx, level) {
    const info = towerLevels[level-1];
    ctx.fillStyle = info.color;
    ctx.strokeStyle = "#222";
    
    if(info.shape === "triangle") {
        ctx.beginPath();
        ctx.moveTo(0, -18);
        ctx.lineTo(15, 12);
        ctx.lineTo(-15, 12);
        ctx.closePath();
        ctx.fill();
        ctx.stroke();
    } else if(info.shape === "square") {
        ctx.fillRect(-15, -15, 30, 30);
        ctx.strokeRect(-15, -15, 30, 30);
    } else if(info.shape === "pentagon") {
        ctx.beginPath();
        for(let k=0;k<5;k++) {
            let angle = Math.PI/2 + k*2*Math.PI/5;
            ctx.lineTo(0+18*Math.cos(angle), 0+18*Math.sin(angle));
        }
        ctx.closePath();
        ctx.fill();
        ctx.stroke();
    } else if(info.shape === "hexagon") {
        ctx.beginPath();
        for(let k=0;k<6;k++) {
            let angle = Math.PI/6 + k*2*Math.PI/6;
            ctx.lineTo(0+18*Math.cos(angle), 0+18*Math.sin(angle));
        }
        ctx.closePath();
        ctx.fill();
        ctx.stroke();
    }
}

function showTowerInfo(t) {
    const info = towerLevels[t.level-1];
    let html = `<b>${info.name}</b><br>
        Niveau : ${t.level}<br>
        Portée : ${info.range}<br>
        <button onclick="sellTower(selectedTower)">Vendre (+${Math.floor(info.price/2)})</button>`;
    if(t.level < towerLevels.length) {
        html += `<button onclick="upgradeTower(selectedTower)">Améliorer (-${towerLevels[t.level].upgrade})</button>`;
    }
    document.getElementById('tower-info').innerHTML = html;
    document.getElementById('tower-info').style.display = '';
}

function sellTower(t) {
    let refund = Math.floor(towerLevels[t.level-1].price/2);
    money += refund;
    towers = towers.filter(x => x !== t);
    updateMoney();
    drawBoard();
    hideTowerInfo();
}

function upgradeTower(t) {
    if(t.level < towerLevels.length && money>=towerLevels[t.level].upgrade) {
        money -= towerLevels[t.level].upgrade;
        t.level++;
        updateMoney();
        drawBoard();
        showTowerInfo(t);
    }
}

function hideTowerInfo() {
    document.getElementById('tower-info').style.display = 'none';
}

function updateMoney() {
    document.getElementById('money').innerText = "Argent : " + money;
}

function updateLives() {
    document.getElementById('lives').innerText = "Vies : " + lives;
}

function updateWaveInfo() {
    document.getElementById('waveinfo').innerText = "Vague : " + wave;
}

function spawnWave() {
    waveActive = true;
    updateWaveInfo();
    for(let k=0;k<waveEnemies;k++) {
        setTimeout(()=>{
            enemies.push({progress:0, hp:waveHp, maxHp:waveHp});
        }, k*700);
    }
}

function nextWave() {
    wave++;
    waveEnemies = Math.floor(waveEnemies*1.3)+1;
    waveHp = Math.floor(waveHp*1.3)+1;
    spawnWave();
}

function checkWave() {
    if(enemies.length === 0 && waveActive) {
        waveActive = false;
        if(waveTimeout) clearTimeout(waveTimeout);
        waveTimeout = setTimeout(()=>{
            nextWave();
        }, 20000);
        setTimeout(()=>{
            if(!waveActive) nextWave();
        }, 60000);
    }
}

// Gestion améliorée du chat
function toggleChat() {
    const content = document.getElementById('chat-content');
    const toggle = document.getElementById('chat-toggle');
    if(content.style.display === "none") {
        content.style.display = "";
        toggle.textContent = "▼";
    } else {
        content.style.display = "none";
        toggle.textContent = "▲";
    }
}

function sendChat() {
    const input = document.getElementById('chat-input');
    const msg = input.value.trim();
    if(msg.length > 0) {
        const params = getUrlParams();
        const code = params.get('code');
        const pseudo = params.get('pseudo');
        socket.emit('game_message', {
            code: code,
            pseudo: pseudo,
            msg: msg
        });
        input.value = "";
    }
}

// Event Listeners et initialisation
document.addEventListener('DOMContentLoaded', function() {
    const params = getUrlParams();
    const code = params.get('code') || 'testroom';
    const pseudo = params.get('pseudo') || 'Joueur';

    // Clic sur le plateau
    document.getElementById('board').onclick = function(e) {
        const rect = this.getBoundingClientRect();
        const mx = e.clientX - rect.left, my = e.clientY - rect.top;
        let clickedOnTower = false;
        
        for(const t of towers) {
            let x = isoX(t.i,t.j), y = isoY(t.i,t.j)+tileH/2;
            if(Math.hypot(mx-x, my-y)<22) {
                selectedTower = t;
                showTowerInfo(t);
                drawBoard();
                clickedOnTower = true;
                break;
            }
        }
        
        if (!clickedOnTower) {
            let minDist = 9999, sel = null;
            for(let i=0;i<rows;i++) for(let j=0;j<cols;j++) {
                let x = isoX(i,j), y = isoY(i,j)+tileH/2;
                let d = Math.hypot(mx-x, my-y);
                if(d<22 && !path.some(cell=>cell.i===i&&cell.j===j) && !towers.some(t=>t.i===i&&t.j===j)) {
                    if(d<minDist) { minDist = d; sel = {i,j}; }
                }
            }
            if(sel && money>=towerLevels[0].price) {
                towers.push({i:sel.i, j:sel.j, level:1});
                money -= towerLevels[0].price;
                updateMoney();
                drawBoard();
            }
            selectedTower = null;
            hideTowerInfo();
        }
    };

    // Configuration du chat
    document.getElementById('chat-send').onclick = sendChat;
    document.getElementById('chat-input').addEventListener('keydown', function(e){
        if(e.key === "Enter") sendChat();
    });

    // Bouton prochaine vague
    document.getElementById('nextwave').onclick = function() {
        if (!waveActive) {
            if (waveTimeout) clearTimeout(waveTimeout);
            nextWave();
        }
    };

    document.body.addEventListener('mousedown', function(e){
        if(e.target.closest('#tower-info')==null && e.target.id!=="board") {
            selectedTower = null;
            hideTowerInfo();
        }
    });

    // Gestion des messages du chat
    socket.on('game_message', data => {
        const div = document.getElementById('chat-messages');
        if (data.pseudo) {
            div.innerHTML += `<div><b>${data.pseudo}:</b> ${data.msg}</div>`;
        } else {
            div.innerHTML += `<div>${data.msg}</div>`;
        }
        div.scrollTop = div.scrollHeight;
    });

    // Animation
    setInterval(()=>{
        for(const e of enemies) {
            e.progress += 0.035 + wave*0.002;
        }
        
        for(const t of towers) {
            const info = towerLevels[t.level-1];
            for(const e of enemies) {
                let pos = path[Math.floor(e.progress)];
                if(!pos) continue;
                let dist = Math.hypot(t.i-pos.i, t.j-pos.j);
                if(dist<=info.range && e.hp>0) {
                    let hitChance = 0.05 + 0.07*(t.level-1);
                    if(Math.random()<hitChance) e.hp--;
                }
            }
        }
        
        for(let i=enemies.length-1;i>=0;i--) {
            if(enemies[i].hp<=0) {
                money += 3;
                enemies.splice(i,1);
                updateMoney();
            } else if(enemies[i].progress>=path.length-1) {
                enemies.splice(i,1);
                lives -= 1;
                updateLives();
                if(lives <= 0) {
                    alert("Partie terminée ! Vous avez perdu.");
                    window.location.reload();
                    return;
                }
            }
        }
        drawBoard();
        checkWave();
    }, 50);

    // Initialisation
    spawnWave();
    updateMoney();
    updateLives();
    drawBoard();
});