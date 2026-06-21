import os

html = open('index.html', 'r', encoding='utf-8').read()

# Add Scripts to HEAD
html = html.replace('</title>', '''</title>
  <script src="/socket.io/socket.io.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/qrcode@1.5.1/build/qrcode.min.js"></script>''')

# Add Multiplayer Lobby Screens to body
lobby_html = '''
  <div id="screen-lobby-host" style="display:none; flex-direction:column; align-items:center; width:100%; margin-top:2rem;">
    <h2 style="color:var(--gold); margin-bottom:1rem; font-size:2rem;">🏠 ルーム作成</h2>
    <p style="font-size:1.2rem; font-weight:bold;">友達にこの数字を入力してもらおう！</p>
    <h1 id="room-pin" style="font-size:5rem; color:var(--text-main); letter-spacing:10px; margin:1rem 0;">----</h1>
    <p style="font-size:1.2rem; font-weight:bold; margin-bottom:1rem;">またはカメラでQRコードをスキャン</p>
    <canvas id="qr-canvas" style="margin-bottom: 2rem; border-radius:12px; border:4px solid white; box-shadow:0 10px 20px rgba(0,0,0,0.1);"></canvas>
    <div id="host-players-list" style="background:white; padding:1.5rem; border-radius:16px; width:100%; max-width:400px; margin-bottom:2rem; font-size:1.5rem; font-weight:bold; color:var(--text-main); text-align:center;">
      <div>👤 あなた (ホスト)</div>
    </div>
    <div style="display:flex; gap:1rem;">
      <button class="btn-secondary" style="font-size:1.2rem;" onclick="showMenu()">← やめる</button>
      <button class="btn-primary" style="font-size:1.2rem;" onclick="startMultiplayerGame()">全員そろったらスタート</button>
    </div>
  </div>

  <div id="screen-lobby-join" style="display:none; flex-direction:column; align-items:center; width:100%; margin-top:2rem;">
    <h2 style="color:var(--basic-btn); margin-bottom:1rem; font-size:2rem;">🚪 ルームに入る</h2>
    <p style="font-size:1.2rem; font-weight:bold; margin-bottom:1rem;">ホストの数字を入れてね</p>
    <input type="text" id="join-pin" placeholder="数字4ケタ" style="font-size:2rem; padding:1rem; text-align:center; width:200px; margin-bottom:1rem; border-radius:12px; border:2px solid #ccc; font-weight:bold;" maxlength="4">
    <input type="text" id="join-name" placeholder="あなたのなまえ" style="font-size:1.5rem; padding:1rem; text-align:center; width:300px; margin-bottom:2rem; border-radius:12px; border:2px solid #ccc; font-weight:bold;">
    <div style="display:flex; gap:1rem;">
      <button class="btn-secondary" style="font-size:1.2rem;" onclick="showMenu()">← やめる</button>
      <button class="btn-primary" style="font-size:1.2rem;" onclick="joinRoom()">部屋に入る</button>
    </div>
    <div id="join-status" style="margin-top:2rem; font-size:1.5rem; color:var(--gold); font-weight:bold;"></div>
  </div>
'''
html = html.replace('<div id="screen-game">', lobby_html + '\n  <div id="screen-game">')

# Modify Main Menu
menu_buttons = '''    <div style="margin-top: 2rem; display: flex; gap: 1rem; justify-content: center; flex-wrap:wrap; max-width:600px;">
      <button class="btn-primary" style="font-size: 1.5rem; padding: 1rem 2rem; width:100%;" onclick="startGame()">1人で遊ぶ (vs CPU)</button>
      <button class="btn-primary" style="font-size: 1.5rem; padding: 1rem 2rem; background:var(--basic-btn); width:48%;" onclick="openHostLobby()">🏠 ルームを作る</button>
      <button class="btn-primary" style="font-size: 1.5rem; padding: 1rem 2rem; background:var(--standard-btn); width:48%;" onclick="openJoinLobby()">🚪 ルームに入る</button>
      <button class="btn-secondary" style="font-size: 1.5rem; padding: 1rem 2rem; border: 4px solid var(--gold); color: var(--gold); width:100%; margin-top:1rem;" onclick="openZukan()">📖 図鑑を見る</button>
    </div>'''
html = html.replace('''    <div style="margin-top: 2rem; display: flex; gap: 1rem; justify-content: center;">
      <button class="btn-primary" style="font-size: 1.5rem; padding: 1.5rem 3rem;" onclick="startGame()">ゲームスタート</button>
      <button class="btn-secondary" style="font-size: 1.5rem; padding: 1.5rem 3rem; border: 4px solid var(--gold); color: var(--gold);" onclick="openZukan()">📖 図鑑を見る</button>
    </div>''', menu_buttons)

multiplayer_logic = '''
// --- Multiplayer State ---
let socket = null;
let isMultiplayer = false;
let isHost = false;
let myRoomCode = '';

if (typeof io !== 'undefined') {
  socket = io();
  
  socket.on('playerJoined', (data) => {
    if (isHost) {
      const avatarIndex = players.length % avatarList.length;
      players.push({ id: data.id, name: data.name, hand: [], isCpu: false, avatar: avatarList[avatarIndex] });
      const list = document.getElementById('host-players-list');
      const div = document.createElement('div');
      div.innerText = `👤 ${data.name} が参加しました`;
      list.appendChild(div);
      showToast(`👤 ${data.name} が参加しました！`);
    }
  });

  socket.on('gameStateUpdate', (state) => {
    if (!isHost) {
      turnIndex = state.turnIndex;
      playDirection = state.playDirection;
      discardPile = state.discardPile;
      players = state.players;
      hasDrawnThisTurn = state.hasDrawnThisTurn;
      renderBoardClient();
    }
  });
  
  socket.on('remotePlayCard', (data) => {
    if (isHost && turnIndex === data.playerIdx) playCard(data.playerIdx, data.cardIdx);
  });
  
  socket.on('remoteDrawCard', (data) => {
    if (isHost && turnIndex === data.playerIdx) drawCardPlayer();
  });
  
  socket.on('remotePassTurn', (data) => {
    if (isHost && turnIndex === data.playerIdx) passTurn();
  });
  
  socket.on('remoteColorSelect', (data) => {
    if (isHost && turnIndex === data.playerIdx) selectColor(data.color);
  });
  
  socket.on('gameEnd', (winner) => {
    if (!isHost) endGame(winner);
  });
}

function openHostLobby() {
  document.getElementById('screen-menu').style.display = 'none';
  document.getElementById('screen-lobby-host').style.display = 'flex';
  document.getElementById('screen-lobby-join').style.display = 'none';
  document.getElementById('screen-game').style.display = 'none';
  
  isMultiplayer = true;
  isHost = true;
  myRoomCode = Math.floor(1000 + Math.random() * 9000).toString();
  document.getElementById('room-pin').innerText = myRoomCode;
  
  if(socket) socket.emit('createRoom', myRoomCode);
  
  const currentUrl = new URL(window.location.href);
  currentUrl.searchParams.set('room', myRoomCode);
  if(typeof QRCode !== 'undefined') {
      QRCode.toCanvas(document.getElementById('qr-canvas'), currentUrl.href, { width: 200, margin: 2 });
  }
  
  players = [{ id: 'player', name: 'あなた (ホスト)', hand: [], isCpu: false, avatar: avatarList[0] }];
  document.getElementById('host-players-list').innerHTML = '<div>👤 あなた (ホスト)</div>';
}

function openJoinLobby() {
  document.getElementById('screen-menu').style.display = 'none';
  document.getElementById('screen-lobby-host').style.display = 'none';
  document.getElementById('screen-lobby-join').style.display = 'flex';
  document.getElementById('screen-game').style.display = 'none';
  
  isMultiplayer = true;
  isHost = false;
  
  const params = new URLSearchParams(window.location.search);
  if (params.has('room')) {
    document.getElementById('join-pin').value = params.get('room');
  }
}

function joinRoom() {
  const pin = document.getElementById('join-pin').value;
  const name = document.getElementById('join-name').value || 'ゲスト';
  if (pin.length < 4) return alert('4ケタの数字を入れてね');
  
  myRoomCode = pin;
  if(socket) socket.emit('joinRoom', pin, name);
  document.getElementById('join-status').innerText = '⏳ ホストがゲームを始めるのを待っています...';
  
  // Actually wait for gameStateUpdate to show game screen
  socket.once('gameStateUpdate', () => {
    document.getElementById('screen-lobby-join').style.display = 'none';
    document.getElementById('screen-game').style.display = 'flex';
  });
}

function startMultiplayerGame() {
  document.getElementById('screen-lobby-host').style.display = 'none';
  document.getElementById('screen-game').style.display = 'flex';
  
  while (players.length < 4) {
    const i = players.length;
    players.push({ id: `cpu${i}`, name: ['たける', 'けんた', 'さくら'][i-1] || `CPU${i}`, hand: [], isCpu: true, avatar: avatarList[i % 3] });
  }
  
  deck = JSON.parse(JSON.stringify(DECK_TEMPLATE));
  deck.sort(() => Math.random() - 0.5);
  discardPile = [];
  
  for (let i = 0; i < 7; i++) {
    players.forEach(p => p.hand.push(deck.pop()));
  }
  
  let top = deck.pop();
  while(top.action) {
    deck.unshift(top);
    top = deck.pop();
  }
  discardPile.push(top);
  
  turnIndex = 0;
  playDirection = 1;
  hasDrawnThisTurn = false;
  
  renderBoard();
  broadcastState();
  startTurn();
}

function broadcastState() {
  if (isMultiplayer && isHost && socket) {
    socket.emit('relay', myRoomCode, 'gameStateUpdate', {
      turnIndex, playDirection, discardPile, players, hasDrawnThisTurn
    });
  }
}

window.clientPlayCard = function(idx) {
  if (turnIndex !== players.findIndex(p => p.id === socket.id)) return;
  socket.emit('relay', myRoomCode, 'remotePlayCard', { playerIdx: turnIndex, cardIdx: idx });
}
window.clientDrawCard = function() {
  if (turnIndex !== players.findIndex(p => p.id === socket.id)) return;
  socket.emit('relay', myRoomCode, 'remoteDrawCard', { playerIdx: turnIndex });
}
window.clientPassTurn = function() {
  socket.emit('relay', myRoomCode, 'remotePassTurn', { playerIdx: turnIndex });
}
window.clientSelectColor = function(col) {
  document.getElementById('color-modal').classList.remove('open');
  socket.emit('relay', myRoomCode, 'remoteColorSelect', { playerIdx: turnIndex, color: col });
}

function renderBoardClient() {
  const myIdx = players.findIndex(p => p.id === socket.id);
  
  const cpuContainer = document.getElementById('cpu-container');
  cpuContainer.innerHTML = '';
  for (let i = 0; i < players.length; i++) {
    if (i === myIdx) continue;
    const p = players[i];
    const div = document.createElement('div');
    div.className = `cpu-player ${turnIndex === i ? 'active' : ''}`;
    div.innerHTML = `
      <img src="${p.avatar || 'avatars/player1_boyA.png'}" class="cpu-avatar" alt="${p.name}">
      <div class="cpu-name">${p.name}</div>
      <div class="cpu-card-count">🂠 ${p.hand.length}</div>
    `;
    cpuContainer.appendChild(div);
  }
  
  const topCard = discardPile[discardPile.length - 1];
  const pileDiv = document.getElementById('discard-pile');
  if (topCard) {
    let twotoneStyleTop = '';
    const cMap = { green: '#22c55e', red: '#ef4444', blue: '#3b82f6', yellow: '#eab308' };
    if (topCard.action === 'wild' && topCard.activeColors) {
      twotoneStyleTop = `background: ${cMap[topCard.activeColors[0]]}; padding: 6px; border-radius: 16px; box-sizing: border-box;`;
    } else if (topCard.color.length === 2) {
      const c1 = cMap[topCard.color[0]];
      const c2 = cMap[topCard.color[1]];
      twotoneStyleTop = `background: linear-gradient(135deg, ${c1} 49%, ${c2} 51%); padding: 6px; border-radius: 16px; box-sizing: border-box;`;
    }
    pileDiv.innerHTML = `<div style="width:100%; height:100%; ${twotoneStyleTop}"><img src="${topCard.img}" style="width: 100%; height: 100%; object-fit: cover; border-radius: 10px; border: 2px solid white;"></div>`;
  }
  
  const pArea = document.getElementById('player-area');
  const myNameLabel = document.querySelector('.player-name');
  if (myIdx >= 0) myNameLabel.innerText = `👤 ${players[myIdx].name} の番`;
  
  if (turnIndex === myIdx) pArea.classList.add('active');
  else pArea.classList.remove('active');
  
  const handDiv = document.getElementById('player-hand');
  handDiv.innerHTML = '';
  
  if (myIdx >= 0) {
    const myHand = players[myIdx].hand;
    myHand.forEach((card, idx) => {
      const playable = isPlayable(card);
      const cardDiv = document.createElement('div');
      cardDiv.className = `playing-card ${turnIndex === myIdx && !hasDrawnThisTurn ? (playable ? 'playable' : 'unplayable') : ''}`;
      
      if (turnIndex === myIdx && playable) cardDiv.className = 'playing-card playable';
      else if (turnIndex === myIdx) cardDiv.className = 'playing-card unplayable';
      else cardDiv.className = 'playing-card';
      
      let twotoneStyle = '';
      const cMap = { green: '#22c55e', red: '#ef4444', blue: '#3b82f6', yellow: '#eab308' };
      if (card.color.length === 2 && !card.action) {
        const c1 = cMap[card.color[0]];
        const c2 = cMap[card.color[1]];
        twotoneStyle = `background: linear-gradient(135deg, ${c1} 49%, ${c2} 51%); padding: 6px; border-radius: 16px; box-sizing: border-box;`;
      }
      
      cardDiv.innerHTML = `<div style="width:100%; height:100%; ${twotoneStyle}"><img src="${card.img}" style="width: 100%; height: 100%; object-fit: cover; border-radius: 10px; border: 2px solid white;"></div>`;
      cardDiv.onclick = () => clientPlayCard(idx);
      handDiv.appendChild(cardDiv);
    });
  }
  
  document.getElementById('btn-pass').style.display = (turnIndex === myIdx && hasDrawnThisTurn) ? 'block' : 'none';
  document.getElementById('btn-pass').onclick = clientPassTurn;
  document.querySelector('.deck').onclick = clientDrawCard;
  
  const currentPlayer = players[turnIndex];
  if(currentPlayer) showTurnIndicator(turnIndex === myIdx ? 'あなたの番！' : `${currentPlayer.name}の番`);
  
  if (turnIndex === myIdx && topCard && topCard.action === 'wild' && !topCard.activeColors) {
     document.getElementById('color-modal').classList.add('open');
     const btns = document.querySelectorAll('#color-modal button');
     btns[0].onclick = () => clientSelectColor('green');
     btns[1].onclick = () => clientSelectColor('red');
     btns[2].onclick = () => clientSelectColor('blue');
     btns[3].onclick = () => clientSelectColor('yellow');
  }
}
'''
html = html.replace('// --- Card Data ---', multiplayer_logic + '\n// --- Card Data ---')

# Fix startGame to disable multiplayer flag
html = html.replace('function startGame() {', '''function startGame() {
  isMultiplayer = false;
  isHost = false;''')

# Broadcast on endgame
html = html.replace("modal.classList.add('open');", '''modal.classList.add('open');
  if (isMultiplayer && isHost && socket) {
    socket.emit('relay', myRoomCode, 'gameEnd', winner);
  }''')

open('index.html', 'w', encoding='utf-8').write(html)
