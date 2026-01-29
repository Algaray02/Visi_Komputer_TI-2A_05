// Nama file ini harus app.js (jika CJS) atau app.cjs (jika ESM)
// Pastikan Next.js adalah dependensi (bukan devDependency) di package.json

const next = require('next');
const http = require('http');

// Tentukan mode berdasarkan NODE_ENV
const dev = process.env.NODE_ENV !== 'production';

// Inisialisasi aplikasi Next.js
const app = next({ dev });
const handle = app.getRequestHandler();

console.log('Memulai server Next.js kustom...');

app.prepare().then(() => {
  const server = http.createServer((req, res) => {
    // Serahkan semua request ke Next.js
    handle(req, res);
  });

  // PENTING: Jangan tentukan port di sini.
  // server.listen(3000) -> JANGAN LAKUKAN INI
  // Biarkan Phusion Passenger (cPanel) yang memberikannya.
  server.listen();

  console.log('Server Next.js siap dan berjalan.');

}).catch(err => {
  console.error('Error memulai server Next.js:', err);
  process.exit(1);
});