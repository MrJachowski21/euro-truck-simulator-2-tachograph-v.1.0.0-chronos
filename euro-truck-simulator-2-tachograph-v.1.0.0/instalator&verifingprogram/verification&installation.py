import os
import sys
import subprocess
import urllib.request
import zipfile
import shutil
import time

class TachoInstaller:
    def __init__(self):
        # Core modules verification (Standard Library components used by the tacho script)
        self.requirements = {
            "tkinter": "Built-in GUI Library",
            "json": "Built-in JSON Parser",
            "urllib": "Built-in URL Request Engine"
        }
        
        # ANSI color codes for raw console output
        self.COLOR_GREEN = "\033[92m"
        self.COLOR_RED = "\033[91m"
        self.COLOR_YELLOW = "\033[93m"
        self.COLOR_BLUE = "\033[94m"
        self.COLOR_RESET = "\033[0m"
        
        # Exact URL for the latest stable 3.2.5 archive release of Funbit's Telemetry Server
        self.telemetry_url = "https://github.com/Funbit/ets2-telemetry-server/archive/3.2.5.zip"

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_header(self):
        print(f"{self.COLOR_BLUE}==================================================={self.COLOR_RESET}")
        print(f"{self.COLOR_BLUE}   CHRONOS TACHOSYSTEM - ENVIRONMENT VERIFIER      {self.COLOR_RESET}")
        print(f"{self.COLOR_BLUE}==================================================={self.COLOR_RESET}\n")

    def check_dependencies(self):
        print("Checking system dependencies & modules:")
        all_passed = True
        
        for module_name, description in self.requirements.items():
            try:
                if module_name == "tkinter":
                    import tkinter
                elif module_name == "json":
                    import json
                elif module_name == "urllib":
                    import urllib.request
                
                print(f" - {module_name:<10} ({description:<25}): {self.COLOR_GREEN}[INSTALLED]{self.COLOR_RESET}")
            except ImportError:
                print(f" - {module_name:<10} ({description:<25}): {self.COLOR_RED}[NOT INSTALLED]{self.COLOR_RESET}")
                all_passed = False
                
        return all_passed

    def install_missing_module(self, module_name):
        print(f"\nAttempting to repair/install environment support for: {module_name}...")
        try:
            if module_name == "tkinter" and os.name != 'nt':
                # On Linux distributions like Ubuntu, tkinter needs apt packages instead of pip
                print(f"{self.COLOR_YELLOW}Notice: On Linux, tkinter usually requires system packages.{self.COLOR_RESET}")
                print("Running: sudo apt-get install python3-tk")
                subprocess.check_call(["sudo", "apt-get", "install", "-y", "python3-tk"])
            else:
                # Standard pip fallback installation
                subprocess.check_call([sys.executable, "-m", "pip", "install", module_name])
            print(f"{self.COLOR_GREEN}Repair execution finished.{self.COLOR_RESET}\n")
        except Exception as e:
            print(f"{self.COLOR_RED}Error during installation: {e}{self.COLOR_RESET}\n")

    def download_telemetry_repository(self):
        print(f"\n{self.COLOR_BLUE}--- FUNBIT ETS2 TELEMETRY SERVER v3.2.5 DEPLOYMENT ---{self.COLOR_RESET}")
        target_dir = input("Enter target directory path to deploy Funbit Telemetry Server: ").strip()
        
        if not target_dir:
            print(f"{self.COLOR_RED}Installation aborted: Invalid path.{self.COLOR_RESET}")
            return

        # Create target structural path if it doesn't exist
        if not os.path.exists(target_dir):
            try:
                os.makedirs(target_dir)
                print(f"Created target directory: {target_dir}")
            except Exception as e:
                print(f"{self.COLOR_RED}Failed to create directory: {e}{self.COLOR_RESET}")
                return

        zip_path = os.path.join(target_dir, "funbit_telemetry_325.zip")
        
        try:
            print(f"{self.COLOR_YELLOW}Downloading Funbit Telemetry Server v3.2.5 Archive from GitHub...{self.COLOR_RESET}")
            print(f"Source: {self.telemetry_url}")
            
            # Secure standard web stream download with custom User-Agent headers to avoid GitHub blocks
            req = urllib.request.Request(self.telemetry_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response, open(zip_path, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)
                
            print(f"{self.COLOR_GREEN}Download complete! Extracting version 3.2.5 archive...{self.COLOR_RESET}")
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(target_dir)
                
            # Clean up the downloaded zip file
            os.remove(zip_path)
            print(f"\n{self.COLOR_GREEN}Funbit Telemetry v3.2.5 successfully deployed to:{self.COLOR_RESET} {target_dir}")
            print(f"{self.COLOR_YELLOW}Next steps to complete setup:{self.COLOR_RESET}")
            print(" 1. Go into the extracted directory folder (usually named 'ets2-telemetry-server-3.2.5').")
            print(" 2. Open the 'server' directory and execute 'Ets2Telemetry.exe' as Administrator.")
            print(" 3. The server will launch and handle automated plugin registration into Euro Truck Simulator 2.")
            
        except Exception as e:
            print(f"{self.COLOR_RED}An error occurred during deployment: {e}{self.COLOR_RESET}")

    def run_menu(self):
        while True:
            self.clear_screen()
            self.print_header()
            env_ok = self.check_dependencies()
            
            print(f"\n{self.COLOR_BLUE}==================================================={self.COLOR_RESET}")
            print("AVAILABLE ACTIONS:")
            print(" [1] Install / Repair missing Python modules manually")
            print(" [2] Download and deploy Funbit ETS2 Telemetry Server v3.2.5")
            print(" [3] Refresh verification status")
            print(" [4] Exit program")
            print(f"{self.COLOR_BLUE}==================================================={self.COLOR_RESET}")
            
            choice = input("Select an option (1-4): ").strip()
            
            if choice == "1":
                mod_to_install = input("\nEnter module/package name to install (e.g. tkinter): ").strip()
                if mod_to_install:
                    self.install_missing_module(mod_to_install)
                input("\nPress Enter to return to menu...")
            elif choice == "2":
                self.download_telemetry_repository()
                input("\nPress Enter to return to menu...")
            elif choice == "3":
                continue
            elif choice == "4":
                print(f"\n{self.COLOR_GREEN}Exiting verification utility. System ready for Chronos Tacho!{self.COLOR_RESET}")
                break
            else:
                print(f"{self.COLOR_RED}Invalid choice! Please select 1, 2, 3, or 4.{self.COLOR_RESET}")
                time.sleep(1.5)

if __name__ == "__main__":
    # Initialize ANSI escape color sequences on classic Windows Command Prompt environments
    if os.name == 'nt':
        os.system('')
        
    installer = TachoInstaller()
    installer.run_menu()