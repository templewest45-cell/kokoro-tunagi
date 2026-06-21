const express = require('express');
const app = express();
const http = require('http').Server(app);
const io = require('socket.io')(http);
const os = require('os');

app.use(express.static(__dirname));

io.on('connection', (socket) => {
  socket.on('createRoom', (roomCode) => {
    socket.join(roomCode);
    console.log(`Room created: ${roomCode}`);
  });
  
  socket.on('joinRoom', (roomCode, playerData) => {
    socket.join(roomCode);
    let name = typeof playerData === 'string' ? playerData : playerData.name;
    console.log(`${name} joined room: ${roomCode}`);
    // Relay full data object to host
    socket.to(roomCode).emit('playerJoined', { id: socket.id, ...playerData });
  });

  socket.on('relay', (roomCode, eventName, data) => {
    socket.to(roomCode).emit(eventName, data);
  });
  
  socket.on('relayTo', (targetId, eventName, data) => {
    io.to(targetId).emit(eventName, data);
  });
});

function getLocalIP() {
  const interfaces = os.networkInterfaces();
  for (const name of Object.keys(interfaces)) {
    for (const iface of interfaces[name]) {
      if (iface.family === 'IPv4' && !iface.internal) {
        return iface.address;
      }
    }
  }
  return 'localhost';
}

const PORT = 3000;
http.listen(PORT, '0.0.0.0', () => {
  const ip = getLocalIP();
  console.log('=========================================');
  console.log('🌟 こころつなぎ 通信サーバーが起動しました！');
  console.log(`📱 スマホやタブレットでアクセスするURL:`);
  console.log(`   http://${ip}:${PORT}`);
  console.log('=========================================');
});
