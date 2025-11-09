#!/usr/bin/env python3
"""
HMI Dashboard Testing Script
Tests the HMI web interface for vulnerabilities
"""

import requests
import sys
from bs4 import BeautifulSoup

# Configuration
HONEYPOT_IP = '192.168.244.138'  # Change to your Windows host IP where Docker is running
HMI_PORT = 5000
BASE_URL = f"http://{HONEYPOT_IP}:{HMI_PORT}"

def test_basic_access():
    """Test 1: Basic HMI access"""
    print("\n[*] Test 1: Basic HMI Access")
    print("-" * 60)
    
    try:
        response = requests.get(BASE_URL, timeout=10)
        print(f"[+] Status Code: {response.status_code}")
        print(f"[+] Content Length: {len(response.content)} bytes")
        print(f"[+] Headers: {dict(response.headers)}")
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.find('title')
        if title:
            print(f"[+] Page Title: {title.text}")
        
        return True
    except requests.exceptions.ConnectionError:
        print("[-] Connection refused - HMI not accessible")
        return False
    except Exception as e:
        print(f"[-] Error: {e}")
        return False

def test_endpoints():
    """Test 2: Look for API endpoints"""
    print("\n[*] Test 2: Endpoint Discovery")
    print("-" * 60)
    
    endpoints = [
        '/api',
        '/api/data',
        '/api/status',
        '/api/registers',
        '/admin',
        '/login',
        '/dashboard',
        '/config',
        '/status'
    ]
    
    found_endpoints = []
    for endpoint in endpoints:
        try:
            url = f"{BASE_URL}{endpoint}"
            response = requests.get(url, timeout=5)
            if response.status_code != 404:
                found_endpoints.append(endpoint)
                print(f"[+] Found: {endpoint} ({response.status_code})")
        except:
            pass
    
    if not found_endpoints:
        print("[-] No additional endpoints found")
    
    return found_endpoints

def test_sensitive_files():
    """Test 3: Check for sensitive files"""
    print("\n[*] Test 3: Sensitive File Discovery")
    print("-" * 60)
    
    files = [
        'robots.txt',
        '.env',
        'config.json',
        'README.md',
        '.git/config',
        'package.json',
        'requirements.txt'
    ]
    
    found_files = []
    for file in files:
        try:
            url = f"{BASE_URL}/{file}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                found_files.append(file)
                print(f"[!] Found sensitive file: {file}")
                print(f"    Content preview: {response.text[:100]}...")
        except:
            pass
    
    if not found_files:
        print("[+] No sensitive files exposed")
    
    return found_files

def test_sql_injection():
    """Test 4: Basic SQL injection attempts"""
    print("\n[*] Test 4: SQL Injection Testing")
    print("-" * 60)
    
    # This is a basic test - real SQL injection testing requires more sophistication
    payloads = [
        "' OR '1'='1",
        "' OR 1=1--",
        "admin'--",
        "1' UNION SELECT NULL--"
    ]
    
    # Test if there's a search or parameter endpoint
    test_urls = [
        f"{BASE_URL}/search?q=test",
        f"{BASE_URL}/api?param=test",
    ]
    
    for url in test_urls:
        for payload in payloads:
            try:
                test_url = f"{url.replace('test', payload)}"
                response = requests.get(test_url, timeout=5)
                # Check for SQL error messages
                if any(error in response.text.lower() for error in ['sql', 'mysql', 'syntax error', 'database']):
                    print(f"[!] Potential SQL injection: {payload}")
            except:
                pass
    
    print("[+] Basic SQL injection test completed")

def test_xss():
    """Test 5: Basic XSS attempts"""
    print("\n[*] Test 5: XSS Testing")
    print("-" * 60)
    
    payloads = [
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert('XSS')>",
        "javascript:alert('XSS')"
    ]
    
    # Test if there's user input
    test_urls = [
        f"{BASE_URL}/search?q=test",
    ]
    
    for url in test_urls:
        for payload in payloads:
            try:
                test_url = f"{url.replace('test', payload)}"
                response = requests.get(test_url, timeout=5)
                if payload in response.text:
                    print(f"[!] Potential XSS vulnerability")
            except:
                pass
    
    print("[+] Basic XSS test completed")

def main():
    """Run all HMI tests"""
    print("=" * 60)
    print("HMI DASHBOARD SECURITY TESTING")
    print(f"Target: {BASE_URL}")
    print("=" * 60)
    
    # Run tests
    if not test_basic_access():
        print("\n[-] HMI not accessible. Check connection and IP address.")
        return
    
    test_endpoints()
    test_sensitive_files()
    test_sql_injection()
    test_xss()
    
    print("\n" + "=" * 60)
    print("[+] HMI testing completed")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Manually browse to: http://{}:{}".format(HONEYPOT_IP, HMI_PORT))
    print("2. Check browser developer tools (F12)")
    print("3. Look for JavaScript files and API calls")
    print("4. Test form submissions if available")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        HONEYPOT_IP = sys.argv[1]
        BASE_URL = f"http://{HONEYPOT_IP}:{HMI_PORT}"
    
    main()

