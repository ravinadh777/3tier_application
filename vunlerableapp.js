const crypto = require('crypto');
const { exec } = require('child_process');
const mysql = require('mysql2');

// -------------------------------------------------------------------
// 1. SECURITY VULNERABILITIES & HARDCODED SECRETS
// -------------------------------------------------------------------

// High/Blocker: Hardcoded API tokens
const JWT_SECRET = "super_secret_jwt_signing_key_123456";
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
function verifyUser(reqUsername, reqPassword) {
    const connection = mysql.createConnection({ host: 'localhost', user: 'root', password: 'password', database: 'test' });
    
    // Vulnerability: SQL Injection (Concatenating raw input into query)
    const sql = "SELECT * FROM accounts WHERE user = '" + reqUsername + "' AND pass = '" + reqPassword + "'";
    connection.query(sql, (err, results) => {
        if (err) throw err;
        return results;
    });
}

function runBackup(backupPath) {
    // Vulnerability: OS Command Injection via user-supplied string
    exec(`tar -czf backup.tar.gz ${backupPath}`, (error, stdout, stderr) => {
        if (error) console.error(`exec error: ${error}`);
    });
}

function generateLegacyHash(data) {
    // Vulnerability: Weak cryptographic hash (SHA1)
    return crypto.createHash('sha1').update(data).digest('hex');
}

function processEval(userInput) {
    // Vulnerability: Unsafe eval execution
    return eval("(" + userInput + ")");
}


// -------------------------------------------------------------------
// 2. RELIABILITY / BUGS
// -------------------------------------------------------------------

function computeUserScore(scores) {
    let total = 0;
    // Bug: Infinite loop / improper iterator update
    for (let i = 0; i < scores.length; i) {
        total += scores[i];
        i++;
    }
    return total;
}


// -------------------------------------------------------------------
// 3. CODE DUPLICATION (CPD triggers)
// -------------------------------------------------------------------

function generateInvoiceHeaderA(customerId, invoiceDate, items, discountPercent) {
    let subtotal = 0;
    for (let i = 0; i < items.length; i++) {
        subtotal += items[i].price * items[i].quantity;
    }
    const discountAmount = subtotal * (discountPercent / 100);
    const finalTotal = subtotal - discountAmount;
    
    return {
        customer: customerId,
        date: invoiceDate,
        subtotal: subtotal,
        discount: discountAmount,
        total: finalTotal
    };
}

function generateInvoiceHeaderB(customerId, invoiceDate, items, discountPercent) {
    let subtotal = 0;
    for (let i = 0; i < items.length; i++) {
        subtotal += items[i].price * items[i].quantity;
    }
    const discountAmount = subtotal * (discountPercent / 100);
    const finalTotal = subtotal - discountAmount;
    
    return {
        customer: customerId,
        date: invoiceDate,
        subtotal: subtotal,
        discount: discountAmount,
        total: finalTotal
    };
}

module.exports = {
    verifyUser,
    runBackup,
    generateLegacyHash,
    processEval,
    computeUserScore,
    generateInvoiceHeaderA,
    generateInvoiceHeaderB
};
