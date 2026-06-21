import os

html = open('index.html', 'r', encoding='utf-8').read()

profile_html = '''
<div id="user-profile-btn" style="position:absolute; top:1rem; right:1rem; display:flex; align-items:center; gap:0.5rem; background:white; padding:0.5rem 1rem; border-radius:99px; box-shadow:0 4px 6px rgba(0,0,0,0.1); cursor:pointer; z-index:100;" onclick="openProfile()">
  <img id="profile-avatar" src="avatars/player1_boyA.png" style="width:32px; height:32px; border-radius:50%; object-fit:cover; border:2px solid var(--gold);">
  <span id="profile-name" style="font-weight:bold; color:var(--text-main); font-size:1.2rem;">あなた</span>
</div>

<div class="modal-overlay" id="profile-modal">
  <div class="modal-content" style="max-width: 400px;">
    <h3 style="margin-bottom: 1.5rem; color: var(--text-main); font-size: 1.8rem;">👤 プロフィール設定</h3>
    <input type="text" id="input-profile-name" placeholder="なまえ" style="font-size:1.5rem; padding:1rem; width:100%; box-sizing:border-box; margin-bottom:1rem; border-radius:12px; border:2px solid #ccc; text-align:center;">
    <p style="margin-bottom: 0.5rem; font-weight:bold; color:var(--text-main);">アイコンをえらんでね</p>
    <div style="display:flex; justify-content:center; gap: 1rem; margin-bottom: 2rem;">
       <img src="avatars/player1_boyA.png" class="avatar-select" onclick="selectAvatar(0)" style="width:64px; height:64px; border-radius:50%; cursor:pointer; border:4px solid transparent; object-fit:cover;">
       <img src="avatars/player2_boyB.png" class="avatar-select" onclick="selectAvatar(1)" style="width:64px; height:64px; border-radius:50%; cursor:pointer; border:4px solid transparent; object-fit:cover;">
       <img src="avatars/player3_girlA.png" class="avatar-select" onclick="selectAvatar(2)" style="width:64px; height:64px; border-radius:50%; cursor:pointer; border:4px solid transparent; object-fit:cover;">
    </div>
    <div style="display:flex; gap:1rem;">
      <button class="btn-secondary" onclick="closeProfile()">キャンセル</button>
      <button class="btn-primary" onclick="saveProfile()">保存する</button>
    </div>
  </div>
</div>
'''

# Insert profile button into app-container
html = html.replace('<div id="screen-menu">', profile_html + '\n  <div id="screen-menu">')

# Insert logic
profile_logic = '''
let userProfile = JSON.parse(localStorage.getItem('kokoroTsunagiProfile')) || { name: 'あなた', avatar: 'avatars/player1_boyA.png' };
let selectedAvatarIndex = 0;

function updateProfileUI() {
  document.getElementById('profile-name').innerText = userProfile.name;
  document.getElementById('profile-avatar').src = userProfile.avatar;
}

function openProfile() {
  document.getElementById('input-profile-name').value = userProfile.name;
  selectedAvatarIndex = avatarList.indexOf(userProfile.avatar);
  if(selectedAvatarIndex < 0) selectedAvatarIndex = 0;
  updateAvatarSelection();
  document.getElementById('profile-modal').classList.add('open');
}

function selectAvatar(idx) {
  selectedAvatarIndex = idx;
  updateAvatarSelection();
}

function updateAvatarSelection() {
  const imgs = document.querySelectorAll('.avatar-select');
  imgs.forEach((img, idx) => {
    img.style.borderColor = idx === selectedAvatarIndex ? 'var(--gold)' : 'transparent';
  });
}

function closeProfile() {
  document.getElementById('profile-modal').classList.remove('open');
}

function saveProfile() {
  const name = document.getElementById('input-profile-name').value || 'あなた';
  userProfile = { name: name, avatar: avatarList[selectedAvatarIndex] };
  localStorage.setItem('kokoroTsunagiProfile', JSON.stringify(userProfile));
  updateProfileUI();
  closeProfile();
}

// Call on load
window.addEventListener('DOMContentLoaded', () => {
  updateProfileUI();
});
'''

# We inject the logic block at the bottom of the script
html = html.replace('// --- Card Data ---', profile_logic + '\n// --- Card Data ---')

# Patch startGame
html = html.replace('''players = [
    { id: 'player', name: 'あなた', hand: [], isCpu: false },''', 
    '''players = [
    { id: 'player', name: userProfile.name, hand: [], isCpu: false, avatar: userProfile.avatar },''')

# Patch openHostLobby
html = html.replace('''players = [{ id: 'player', name: 'あなた (ホスト)', hand: [], isCpu: false, avatar: avatarList[0] }];
  document.getElementById('host-players-list').innerHTML = '<div>👤 あなた (ホスト)</div>';''',
  '''players = [{ id: 'player', name: userProfile.name + ' (ホスト)', hand: [], isCpu: false, avatar: userProfile.avatar }];
  document.getElementById('host-players-list').innerHTML = `<div style="display:flex; align-items:center; justify-content:center; gap:0.5rem;"><img src="${userProfile.avatar}" style="width:32px; height:32px; border-radius:50%; object-fit:cover;"> ${userProfile.name} (ホスト)</div>`;''')

# Patch openJoinLobby
html = html.replace('''isMultiplayer = true;
  isHost = false;''',
  '''isMultiplayer = true;
  isHost = false;
  document.getElementById('join-name').value = userProfile.name;''')

# Patch joinRoom
html = html.replace("if(socket) socket.emit('joinRoom', pin, name);", "if(socket) socket.emit('joinRoom', pin, { name: name, avatar: userProfile.avatar });")

# Patch socket playerJoined event
html = html.replace('''const avatarIndex = players.length % avatarList.length;
      players.push({ id: data.id, name: data.name, hand: [], isCpu: false, avatar: avatarList[avatarIndex] });
      const list = document.getElementById('host-players-list');
      const div = document.createElement('div');
      div.innerText = `👤 ${data.name} が参加しました`;''',
      '''players.push({ id: data.id, name: data.name, hand: [], isCpu: false, avatar: data.avatar || avatarList[0] });
      const list = document.getElementById('host-players-list');
      const div = document.createElement('div');
      div.style.display = "flex"; div.style.alignItems = "center"; div.style.justifyContent = "center"; div.style.gap = "0.5rem";
      div.innerHTML = `<img src="${data.avatar || avatarList[0]}" style="width:32px; height:32px; border-radius:50%; object-fit:cover;"> ${data.name} が参加しました`;''')

# One final fix: In openHostLobby, we hide the profile button, and show it again in showMenu
html = html.replace("document.getElementById('screen-lobby-host').style.display = 'flex';", "document.getElementById('screen-lobby-host').style.display = 'flex'; document.getElementById('user-profile-btn').style.display = 'none';")
html = html.replace("document.getElementById('screen-lobby-join').style.display = 'flex';", "document.getElementById('screen-lobby-join').style.display = 'flex'; document.getElementById('user-profile-btn').style.display = 'none';")
html = html.replace("document.getElementById('screen-game').style.display = 'flex';", "document.getElementById('screen-game').style.display = 'flex'; document.getElementById('user-profile-btn').style.display = 'none';")

# We need to show the profile button when going to menu
html = html.replace("document.getElementById('screen-menu').style.display = 'flex';", "document.getElementById('screen-menu').style.display = 'flex'; document.getElementById('user-profile-btn').style.display = 'flex';")

open('index.html', 'w', encoding='utf-8').write(html)
