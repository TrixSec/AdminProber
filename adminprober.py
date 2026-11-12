# Copyright (c) 2024 AdminProber developers
# See the file 'LICENSE' for copying permission.

import requests
from threading import Thread
import queue
import argparse
from pathlib import Path
from termcolor import colored
import sys
import signal
from urllib.parse import urljoin
import os
import time

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

PROBER_VERSION = "1.1" # has to be string, because you are checking 1.1 == "1.1" -- always gonna be false
AUTHOR = "Trix Cyrus"
COPYRIGHT = "Copyright © 2024 Trixsec Org"

def handle_interrupt(signal, frame):
    print(colored("\n[", "white") + colored("INFO", "green", attrs=["bold"]) + colored("] Scan interrupted by user. Exiting...", "red", attrs=["bold"]))
    sys.exit(0)


signal.signal(signal.SIGINT, handle_interrupt)


def check_internet_connection():
    """Check if there's an active internet connection."""
    try:
        requests.get("https://www.google.com", timeout=5)
        print(colored("[", "white") + colored("INFO", "green", attrs=["bold"]) + colored("] Internet connection verified.", "green", attrs=["bold"]))
    except requests.ConnectionError:
        print(colored("[", "white") + colored("INFO", "green", attrs=["bold"]) + colored("] No internet connection. Please check your connection and try again.", "red", attrs=["bold"]))
        sys.exit(1)


def check_for_updates():
    try:
        response = requests.get("https://raw.githubusercontent.com/TrixSec/AdminProber/main/VERSION")
        response.raise_for_status()
        latest_version = response.text.strip()

        if PROBER_VERSION != latest_version:
            print(colored(f"[•] New version available: {latest_version}. Updating...", 'yellow'))
            os.system('git reset --hard HEAD')
            os.system('git pull')
            with open('VERSION', 'w') as version_file:
                version_file.write(latest_version)
            print(colored("[•] Update completed. Please rerun AdminProber.", 'green'))
            exit()

        print(colored(f"[•] You are using the latest version: {latest_version}.", 'green'))
    except requests.RequestException as e:
        print(colored(f"[×] Error fetching the latest version: {e}. Please check your internet connection.", 'red'))

def print_banner():
    banner = r"""
 $$$$$$\        $$\               $$\           $$$$$$$\                      $$\                           
$$  __$$\       $$ |              \__|          $$  __$$\                     $$ |                          
$$ /  $$ | $$$$$$$ |$$$$$$\$$$$\  $$\ $$$$$$$\  $$ |  $$ | $$$$$$\   $$$$$$\  $$$$$$$\   $$$$$$\   $$$$$$\  
$$$$$$$$ |$$  __$$ |$$  _$$  _$$\ $$ |$$  __$$\ $$$$$$$  |$$  __$$\ $$  __$$\ $$  __$$\ $$  __$$\ $$  __$$\ 
$$  __$$ |$$ /  $$ |$$ / $$ / $$ |$$ |$$ |  $$ |$$  ____/ $$ |  \__|$$ /  $$ |$$ |  $$ |$$$$$$$$ |$$ |  \__|
$$ |  $$ |$$ |  $$ |$$ | $$ | $$ |$$ |$$ |  $$ |$$ |      $$ |      $$ |  $$ |$$ |  $$ |$$   ____|$$ |      
$$ |  $$ |\$$$$$$$ |$$ | $$ | $$ |$$ |$$ |  $$ |$$ |      $$ |      \$$$$$$  |$$$$$$$  |\$$$$$$$\ $$ |      
\__|  \__| \_______|\__| \__| \__|\__|\__|  \__|\__|      \__|       \______/ \_______/  \_______|\__|      
    """
    print(colored(banner, 'cyan'))
    print(colored(f"AdminProber Version: {PROBER_VERSION}", 'yellow'))
    print(colored(f"Made by {AUTHOR}", 'yellow'))
    print(colored(COPYRIGHT, 'yellow'))

def load_admin_paths(filepath="wordlist/admin_paths.txt"):
    """Load admin paths from a file."""
    if not Path(filepath).exists():
        raise FileNotFoundError(colored(f"[", "white") + colored("INFO", "green", attrs=["bold"]) + colored(f"] Admin paths file not found: {filepath}", "red", attrs=["bold"]))
    with open(filepath, "r") as f:
        return [line.strip() for line in f if line.strip()]


def scan_url(target_url, path_queue, results, timeout=5):
    """Scan a single URL."""
    while not path_queue.empty():
        path = path_queue.get()
        url = urljoin(target_url, path)
        try:
            print(colored("[", "white") + colored("INFO", "green", attrs=["bold"]) + colored(f"] Testing {url}", "red", attrs=["bold"]))  
            response = requests.get(url, timeout=timeout, allow_redirects=True, verify=False) # careful with this one
            status_code = response.status_code
            page_content = response.text.lower()

            if status_code in [200, 301, 302] and ("admin" in page_content or "login" in page_content):
                print(colored(f"Admin panel found: {url}", "green", attrs=["bold"]))
                results.append((url, status_code)) 
        except requests.RequestException:
            pass 
        finally:
            path_queue.task_done()


def admin_finder(target, threads, paths_file, output_file):
    """Main admin panel finder function."""
    print(colored("\n[", "white") + colored("INFO", "green", attrs=["bold"]) + colored(f"] Starting admin panel scan on: {target}", "cyan", attrs=["bold"]))
    admin_paths = load_admin_paths(paths_file)
    path_queue = queue.Queue()

    path_chunks = [admin_paths[i::threads] for i in range(threads)]
    for paths in path_chunks:
        for path in paths:
            path_queue.put(path)

    results = []
    thread_list = []

    output_dir = Path(output_file).parent
    if not output_dir.exists():
        print(colored("[", "white") + colored("INFO", "green", attrs=["bold"]) + colored(f"] Creating directory: {output_dir}", "yellow", attrs=["bold"]))
        output_dir.mkdir(parents=True, exist_ok=True)

    for _ in range(threads):
        thread = Thread(target=scan_url, args=(target, path_queue, results))
        thread_list.append(thread)
        thread.start()

    for thread in thread_list:
        thread.join()

    if results:
        print(colored("\n[", "white") + colored("INFO", "green", attrs=["bold"]) + colored("] Found admin panels:", "green", attrs=["bold"]))
        for url, status_code in results:
            print(colored(f" - {url} (Status: {status_code})", "green", attrs=["bold"]))
        with open(output_file, "w") as f:
            for url, status_code in results:
                f.write(f"{url} | Status: {status_code}\n")
    else:
        print(colored("\n[", "white") + colored("INFO", "green", attrs=["bold"]) + colored("] No admin panels found.", "yellow", attrs=["bold"]))
    print(colored("\n[", "white") + colored("INFO", "green", attrs=["bold"]) + colored(f"] Results saved to {output_file}", "cyan", attrs=["bold"]))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Admin Panel Finder Tool")
    parser.add_argument("--target", "-t", required=True, help="Target website URL (e.g., https://example.com)")
    parser.add_argument("--threads", "-th", type=int, default=5, help="Number of threads (default: 5)")
    parser.add_argument("--paths", "-p", default="wordlist/admin_paths.txt", help="Path to admin paths file")
    parser.add_argument("--output", "-o", default="results/admin_results.txt", help="File to save results")
    parser.add_argument("--check-updates", "-cu", action="store_true", help="Check for updates")
    args = parser.parse_args()

    if args.check_updates:
        check_for_updates()
        sys.exit()

    print_banner()
    check_internet_connection()

    try:
        admin_finder(args.target, args.threads, args.paths, args.output)
    except Exception as e:
        print(colored("[", "white") + colored("INFO", "green", attrs=["bold"]) + colored(f"] {str(e)}", "red", attrs=["bold"]))
    print(colored("[", "white") + colored("INFO", "green", attrs=["bold"]) + colored("] Scanning complete.", "cyan", attrs=["bold"]))

