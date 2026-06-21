import os

html = open('index.html', 'r', encoding='utf-8').read()

zukan_modal = """
<div class="modal-overlay" id="zukan-modal">
  <div class="modal-content" style="max-width: 800px; max-height: 90vh;">
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 1rem;">
      <h3 style="color: var(--text-main); font-size: 1.8rem;">📖 感情カード図鑑</h3>
      <button class="btn-secondary" onclick="closeZukan()">✖ 閉じる</button>
    </div>
    <div style="margin-bottom: 1rem; font-weight: bold; font-size: 1.2rem; color: var(--gold);">
      集めたカード: <span id="zukan-count">0</span> / 88
    </div>
    <div id="zukan-grid" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(80px, 1fr)); gap: 10px; padding: 10px; overflow-y: auto; max-height: 60vh; background: #f8fafc; border-radius: 12px; border: 2px solid #e2e8f0;">
      <!-- Cards rendered here -->
    </div>
  </div>
</div>
"""

# Insert Zukan Modal right before the Color Modal
html = html.replace('<div class="modal-overlay" id="color-modal">', zukan_modal + '\n<div class="modal-overlay" id="color-modal">')

# Add button to menu
menu_buttons = """    <div style="margin-top: 2rem; display: flex; gap: 1rem; justify-content: center;">
      <button class="btn-primary" style="font-size: 1.5rem; padding: 1.5rem 3rem;" onclick="startGame()">ゲームスタート</button>
      <button class="btn-secondary" style="font-size: 1.5rem; padding: 1.5rem 3rem; border: 4px solid var(--gold); color: var(--gold);" onclick="openZukan()">📖 図鑑を見る</button>
    </div>"""

html = html.replace('''    <div style="margin-top: 2rem;">
      <button class="btn-primary" style="font-size: 1.5rem; padding: 1.5rem 4rem;" onclick="startGame()">ゲームスタート</button>
    </div>''', menu_buttons)

# Add logic
logic = """
let unlockedCards = JSON.parse(localStorage.getItem('kokoroTsunagiUnlocked') || '[]');

function unlockCard(cardId) {
  if (!unlockedCards.includes(cardId)) {
    unlockedCards.push(cardId);
    localStorage.setItem('kokoroTsunagiUnlocked', JSON.stringify(unlockedCards));
  }
}

function openZukan() {
  const grid = document.getElementById('zukan-grid');
  grid.innerHTML = '';
  
  // Sort and display unique template cards
  const uniqueCards = [];
  const seenIds = new Set();
  DECK_TEMPLATE.forEach(c => {
    // Action cards have 4 copies with _0, _1 etc, just show one generic or all 4? 
    // Actually standard cards are Joy_1 to Joy_15. They are all unique.
    // Action cards are Action_Skip_0 to 3. Let's just group actions as Action_Skip, Action_Reverse etc.
    let baseId = c.id;
    if (c.action) {
       baseId = c.id.substring(0, c.id.lastIndexOf('_')); // e.g. Action_Skip
    }
    
    if (!seenIds.has(baseId)) {
      seenIds.add(baseId);
      // For action cards, we treat ANY unlocked Action_Skip_X as unlocking Action_Skip.
      // So let's check if the user has unlocked ANY card matching this baseId
      const isUnlocked = unlockedCards.some(uc => uc.startsWith(baseId));
      
      const div = document.createElement('div');
      div.style.aspectRatio = "55/91";
      div.style.borderRadius = "8px";
      div.style.overflow = "hidden";
      div.style.boxShadow = "0 4px 6px rgba(0,0,0,0.1)";
      
      if (isUnlocked) {
        div.innerHTML = `<img src="${c.img}" style="width:100%; height:100%; object-fit:cover;">`;
      } else {
        div.innerHTML = `<div style="width:100%; height:100%; background:#cbd5e1; display:flex; align-items:center; justify-content:center; color:white; font-weight:bold; font-size:2rem;">?</div>`;
      }
      grid.appendChild(div);
    }
  });
  
  // Actually there are 15x4 = 60 standard, 12 complex, 4 action types = 76 unique types.
  document.getElementById('zukan-count').innerText = seenIds.size; // Total unique types is 76!
  
  // Re-calculate unlocked count based on baseIds
  const unlockedBaseIds = new Set();
  unlockedCards.forEach(uc => {
    if (uc.startsWith('Action_')) {
      unlockedBaseIds.add(uc.substring(0, uc.lastIndexOf('_')));
    } else {
      unlockedBaseIds.add(uc);
    }
  });
  document.getElementById('zukan-count').innerText = unlockedBaseIds.size;
  
  document.getElementById('zukan-modal').classList.add('open');
}

function closeZukan() {
  document.getElementById('zukan-modal').classList.remove('open');
}
"""

html = html.replace('// --- Game State ---', logic + '\n// --- Game State ---')

# Inject unlockCard() calls
html = html.replace('''    players.forEach(p => {
      p.hand.push(deck.pop());
    });''', '''    players.forEach(p => {
      const c = deck.pop();
      p.hand.push(c);
      if (!p.isCpu) unlockCard(c.id);
    });''')

html = html.replace('''  const card = deck.pop();
  players[0].hand.push(card);
  hasDrawnThisTurn = true;''', '''  const card = deck.pop();
  players[0].hand.push(card);
  unlockCard(card.id);
  hasDrawnThisTurn = true;''')

# Write back
open('index.html', 'w', encoding='utf-8').write(html)
