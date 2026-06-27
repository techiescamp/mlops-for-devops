const { createProxyMiddleware } = require('http-proxy-middleware')
const { config } = require('./config')

module.exports = function(app) {
    app.use('/api', createProxyMiddleware({
        target: config.base_url,
        changeOrigin: true
    }))
}