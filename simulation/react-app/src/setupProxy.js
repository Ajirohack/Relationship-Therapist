const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function (app) {
  app.use(
    '/api',
    createProxyMiddleware({
      target: 'http://localhost:8001',  // Updated port from 8000 to 8001
      changeOrigin: true,
      pathRewrite: {
        '^/api': '' // Remove the /api prefix when forwarding to the target
      },
      logLevel: 'debug'
    })
  );
};