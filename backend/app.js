const express = require('express');
const fs = require('fs');
const path = require('path');
const session = require('express-session');

const app = express();
app.use(express.json());

// -------------------------------------------------------------
// 1. SECURITY HOTSPOTS & VULNERABILITIES
// -------------------------------------------------------------

// Security Hotspot: Insecure session cookie configuration
app.use(session({
    secret: 'insecure_session_secret_xyz',
    resave: false,
    saveUninitialized: true,
    cookie: { secure: false, httpOnly: false } // Flagged by SonarQube
}));

// Vulnerability: Path Traversal / Arbitrary File Read
app.get('/download', (req, res) => {
    const userFile = req.query.filename;
    const targetPath = path.join(__dirname, 'public', userFile); // No sanitization
    res.sendFile(targetPath);
});

// Vulnerability: Reflected XSS (Writing unescaped user input to response body)
app.get('/search', (req, res) => {
    const term = req.query.q;
    res.send(`<h1>Search Results for: ${term}</h1>`);
});

// Vulnerability: Regular Expression Denial of Service (ReDoS)
app.post('/validate-email', (req, res) => {
    const emailRegex = /^([a-zA-Z0-9_\.\-])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+$/;
    const isValid = emailRegex.test(req.body.email);
    res.json({ valid: isValid });
});

// -------------------------------------------------------------
// 2. RELIABILITY / CODE SMELLS
// -------------------------------------------------------------

// Code Smell: Useless assignment / Empty catch block
function processUserData(input) {
    let result = "";
    try {
        result = JSON.parse(input);
    } catch (e) {
        // Ignored exception (SonarQube flags empty catch blocks)
    }
    return result;
}

app.listen(3000, () => {
    console.log('Server running on port 3000');
});
