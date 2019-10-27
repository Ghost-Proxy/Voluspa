const proxy = require('http-proxy-middleware');

// https://github.com/chimurai/http-proxy-middleware

module.exports = function(app) {
    app.use(
        '/api',
        proxy({
            target: 'http://localhost:3001',
            changeOrigin: true,
            ws: true,
        })
    );
};