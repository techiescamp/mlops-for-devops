const express = require('express')
const path = require('path')
const { createProxyMiddleware } = require('http-proxy-middleware')

const app = express()
const PORT = 3000

// serve static file
app.use(express.static(path.join(__dirname, 'build'))) // ../frontend/build

// proxy /api to your backend
app.use('/api', createProxyMiddleware({
    target: process.env.REACT_APP_API_URL || 'http://localhost:8000',
    changeOrigin: true
}))

console.log('process.env.REACT_APP_API_URL', process.env.REACT_APP_API_URL)

app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, 'build', 'index.html')) // ..frontend/build/index.html
})

app.listen(PORT || 3000, () => {
    console.log(`Server is running at PORT: ${PORT}`)
})