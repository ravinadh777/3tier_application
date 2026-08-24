import hashlib
import os
import sqlite3
import subprocess

# -------------------------------------------------------------------
# 1. SECURITY VULNERABILITIES & HARDCODED SECRETS
# -------------------------------------------------------------------

# High/Blocker: Hardcoded credentials
AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
DB_PASSWORD = "SuperSecretPassword123!"

def authenticate_user(username, password):
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    
    # Vulnerability: SQL Injection via unsanitized query string
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    cursor.execute(query)
    return cursor.fetchone()

def execute_ping(host_ip):
    # Vulnerability: Command Injection (shell=True with unvalidated user input)
    subprocess.run(f"ping -c 1 {host_ip}", shell=True, check=True)

def insecure_hash(raw_text):
    # Vulnerability: Weak cryptographic algorithm (MD5)
    return hashlib.md5(raw_text.encode()).hexdigest()


# -------------------------------------------------------------------
# 2. RELIABILITY / BUGS
# -------------------------------------------------------------------

def read_system_metrics(filename):
    # Reliability: Resource leak (file is opened but never closed)
    f = open(filename, "r")
    data = f.read()

    # Reliability: ZeroDivisionError & unreachable code
    flag = 0
    if flag == 0:
        return data
    calc = 50 / flag
    return calc


# -------------------------------------------------------------------
# 3. CODE DUPLICATION (CPD triggers)
# -------------------------------------------------------------------

def calculate_monthly_tax_bracket_standard(income, allowances, deductions, standard_rate):
    taxable_base = income - allowances - deductions
    if taxable_base < 0:
        taxable_base = 0
    calculated_tax = taxable_base * standard_rate
    effective_income = income - calculated_tax
    
    summary = {
        "gross": income,
        "taxable": taxable_base,
        "tax_amount": calculated_tax,
        "net_payout": effective_income
    }
    return summary

def calculate_monthly_tax_bracket_corporate(income, allowances, deductions, standard_rate):
    taxable_base = income - allowances - deductions
    if taxable_base < 0:
        taxable_base = 0
    calculated_tax = taxable_base * standard_rate
    effective_income = income - calculated_tax
    
    summary = {
        "gross": income,
        "taxable": taxable_base,
        "tax_amount": calculated_tax,
        "net_payout": effective_income
    }
    return summary
