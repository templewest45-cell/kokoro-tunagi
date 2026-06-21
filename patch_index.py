import os

html = open('index.html', 'r', encoding='utf-8').read()

html = html.replace('<!-- Result Modal -->', '''<div id="toast" style="position:fixed; top:20px; left:50%; transform:translateX(-50%); background:rgba(0,0,0,0.8); color:white; padding:1rem 2rem; border-radius:999px; font-weight:bold; font-size:1.2rem; z-index:2000; opacity:0; pointer-events:none; transition:opacity 0.3s;"></div>

<div class="modal-overlay" id="color-modal">
  <div class="modal-content" style="max-width: 400px;">
    <h3 style="margin-bottom: 1.5rem; color: var(--text-main);">🌈 好きな色を選んでね</h3>
    <div style="display:flex; justify-content:center; gap: 1rem;">
       <button class="btn-primary" style="background:#22c55e" onclick="selectColor('green')">緑</button>
       <button class="btn-primary" style="background:#ef4444" onclick="selectColor('red')">赤</button>
       <button class="btn-primary" style="background:#3b82f6" onclick="selectColor('blue')">青</button>
       <button class="btn-primary" style="background:#eab308" onclick="selectColor('yellow')">黄</button>
    </div>
  </div>
</div>

<!-- Result Modal -->''')

html = html.replace('DECK_TEMPLATE.push({ id: `Complex_${i}`, color: complexColors[i-1], img: `cards_output_print/Wildcard_${i}_print.png` });\n}', '''DECK_TEMPLATE.push({ id: `Complex_${i}`, color: complexColors[i-1], img: `cards_output_print/Wildcard_${i}_print.png` });\n}

const colorsForAction = ['green', 'red', 'blue', 'yellow'];
colorsForAction.forEach(col => {
  DECK_TEMPLATE.push({ id: `Action_Skip_${col}`, color: [col], action: 'skip', name: 'ひとやすみ', img: `cards_output_print/Action_1.png` });
  DECK_TEMPLATE.push({ id: `Action_Reverse_${col}`, color: [col], action: 'reverse', name: 'きりかえ！', img: `cards_output_print/Action_2.png` });
  DECK_TEMPLATE.push({ id: `Action_Draw2_${col}`, color: [col], action: 'draw2', name: 'おすそわけ', img: `cards_output_print/Action_3.png` });
});
for (let i = 0; i < 4; i++) {
  DECK_TEMPLATE.push({ id: `Action_Wild_${i}`, color: ['wild'], action: 'wild', name: 'きもちチェンジ', img: `cards_output_print/Action_4.png` });
}''')

html = html.replace('let hasDrawnThisTurn = false;', 'let hasDrawnThisTurn = false;\nlet playDirection = 1;\n\nfunction showToast(msg) {\n  const t = document.getElementById("toast");\n  t.innerHTML = msg;\n  t.style.opacity = 1;\n  setTimeout(() => t.style.opacity = 0, 2000);\n}')

html = html.replace('''// First card to discard pile
  discardPile.push(deck.pop());
  
  turnIndex = 0;''', '''// First card to discard pile
  let top = deck.pop();
  while(top.action) {
    deck.unshift(top);
    top = deck.pop();
  }
  discardPile.push(top);
  
  turnIndex = 0;
  playDirection = 1;''')

html = html.replace('if (topCard.color.length === 2) {', '''if (topCard.action === 'wild' && topCard.activeColors) {
      twotoneStyleTop = `background: ${cMap[topCard.activeColors[0]]}; padding: 6px; border-radius: 16px; box-sizing: border-box;`;
    } else if (topCard.color.length === 2) {''')

html = html.replace('if (card.color.length === 2) {', '''if (card.action && card.color[0] !== 'wild') {
      twotoneStyle = `background: ${cMap[card.color[0]]}; padding: 6px; border-radius: 16px; box-sizing: border-box;`;
    } else if (card.color.length === 2) {''')

html = html.replace('''function isPlayable(card) {
  const topCard = discardPile[discardPile.length - 1];
  
  // 色が同じなら出せる
  if (card.color.some(c => topCard.color.includes(c))) return true;
  
  // 数字が同じなら出せる
  const cardNumber = card.id.split('_')[1];
  const topNumber = topCard.id.split('_')[1];
  if (cardNumber === topNumber) return true;
  
  return false;
}''', '''function isPlayable(card) {
  const topCard = discardPile[discardPile.length - 1];
  
  if (card.action === 'wild') return true;

  const validColors = topCard.activeColors || topCard.color;
  
  if (card.color.some(c => validColors.includes(c))) return true;
  
  if (card.action && topCard.action && card.action === topCard.action) return true;
  
  if (!card.action && !topCard.action) {
    const cardNumber = card.id.split('_')[1];
    const topNumber = topCard.id.split('_')[1];
    if (cardNumber === topNumber) return true;
  }
  
  return false;
}''')

html = html.replace('function startTurn() {', '''function getNextTurnIndex() {
  return (turnIndex + playDirection + players.length) % players.length;
}

function refillDeck() {
  const topCard = discardPile.pop();
  deck = discardPile.sort(() => Math.random() - 0.5);
  discardPile = [topCard];
}

function selectColor(color) {
  document.getElementById('color-modal').classList.remove('open');
  const topCard = discardPile[discardPile.length - 1];
  topCard.activeColors = [color];
  const colorNames = {green: '緑', red: '赤', blue: '青', yellow: '黄'};
  showToast(`🌈 きもちチェンジ！ ${colorNames[color]} になった！`);
  renderBoard();
  setTimeout(nextTurn, 1000);
}

function applyCardAction(card) {
  if (!card.action) {
    setTimeout(nextTurn, 1000);
    return;
  }
  
  if (card.action === 'reverse') {
    playDirection *= -1;
    showToast('🔄 きりかえ！（順番が逆に！）');
    setTimeout(nextTurn, 1500);
  } else if (card.action === 'skip') {
    turnIndex = getNextTurnIndex();
    showToast('☕ ひとやすみ！（次の人は1回休み）');
    setTimeout(nextTurn, 1500);
  } else if (card.action === 'draw2') {
    const nextPlayerIdx = getNextTurnIndex();
    const nextPlayer = players[nextPlayerIdx];
    for(let i=0; i<2; i++) {
        if(deck.length === 0) refillDeck();
        nextPlayer.hand.push(deck.pop());
    }
    turnIndex = nextPlayerIdx;
    showToast(`🎁 おすそわけ！ ${nextPlayer.name} は2枚引いた`);
    setTimeout(nextTurn, 1500);
  } else if (card.action === 'wild') {
    if (players[turnIndex].isCpu) {
      const cols = ['green', 'red', 'blue', 'yellow'];
      card.activeColors = [cols[Math.floor(Math.random() * cols.length)]];
      const colorNames = {green: '緑', red: '赤', blue: '青', yellow: '黄'};
      showToast(`🌈 きもちチェンジ！ ${colorNames[card.activeColors[0]]} になった！`);
      renderBoard();
      setTimeout(nextTurn, 1500);
    } else {
      document.getElementById('color-modal').classList.add('open');
    }
  }
}

function startTurn() {''')

html = html.replace('function passTurn() {\n  if (turnIndex !== 0) return;\n  nextTurn();\n}', 'function passTurn() {\n  if (turnIndex !== 0) return;\n  setTimeout(nextTurn, 500);\n}')

html = html.replace('''  if (player.hand.length === 0) {
    endGame(player);
    return;
  }
  
  nextTurn();
}''', '''  if (player.hand.length === 0) {
    endGame(player);
    return;
  }
  
  applyCardAction(card);
}''')

html = html.replace('''    if (cpu.hand.length === 0) {
      endGame(cpu);
      return;
    }
  } else {
    // Draw card
    if (deck.length === 0) {
      const topCard = discardPile.pop();
      deck = discardPile.sort(() => Math.random() - 0.5);
      discardPile = [topCard];
    }''', '''    if (cpu.hand.length === 0) {
      endGame(cpu);
      return;
    }
    applyCardAction(card);
    return;
  } else {
    // Draw card
    if (deck.length === 0) refillDeck();''')

html = html.replace('''function nextTurn() {
  turnIndex = (turnIndex + 1) % players.length;
  startTurn();
}''', '''function nextTurn() {
  turnIndex = getNextTurnIndex();
  startTurn();
}''')

html = html.replace('''  if (deck.length === 0) {
    // Reshuffle discard pile
    const topCard = discardPile.pop();
    deck = discardPile.sort(() => Math.random() - 0.5);
    discardPile = [topCard];
  }''', '  if (deck.length === 0) refillDeck();')

open('index.html', 'w', encoding='utf-8').write(html)
