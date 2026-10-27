import os
import json
import sys
import subprocess
import winreg
import argparse
from pathlib import Path
try:
    from rich.console import Console
    from rich.prompt import Prompt, Confirm
    from rich.panel import Panel
    from rich.text import Text
    from rich.theme import Theme
except ImportError:
    print("The 'rich' library is required. Please install it by running: pip install rich")
    sys.exit(1)

custom_theme = Theme({
    "info": "dim cyan",
    "warning": "magenta",
    "danger": "bold red",
    "success": "bold green"
})
console = Console(theme=custom_theme)

CONFIG_FILE = os.path.expanduser("~/.agy_profiles.json")
DEFAULT_EXE = os.path.expandvars(r"%LOCALAPPDATA%\Programs\Antigravity IDE\Antigravity.exe")
DEFAULT_DESKTOP = os.path.expandvars(r"%USERPROFILE%\Desktop\Users")
BIN_DIR = os.path.expanduser(r"~\bin")

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {}

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

def ensure_in_path():
    """Adds the bin directory to the user's PATH environment variable if missing."""
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_ALL_ACCESS)
        path_value, _ = winreg.QueryValueEx(key, "PATH")
        
        paths = [p.strip() for p in path_value.split(';') if p.strip()]
        if BIN_DIR not in paths:
            paths.append(BIN_DIR)
            new_path = ";".join(paths)
            winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, new_path)
            # Notify OS about environment change (broadcast)
            import ctypes
            HWND_BROADCAST = 0xFFFF
            WM_SETTINGCHANGE = 0x001A
            ctypes.windll.user32.SendMessageW(HWND_BROADCAST, WM_SETTINGCHANGE, 0, 'Environment')
            return True
        winreg.CloseKey(key)
    except Exception as e:
        console.print(f"[danger]Failed to update PATH registry:[/danger] {e}")
    return False

def install_cli():
    """Installs the agy-profiles command wrapper in a bin directory and adds to PATH."""
    os.makedirs(BIN_DIR, exist_ok=True)
    bat_path = os.path.join(BIN_DIR, "agy-profiles.bat")
    
    python_exe = sys.executable
    script_path = os.path.abspath(__file__)
    
    bat_content = f'@echo off\n"{python_exe}" "{script_path}" %*'
    with open(bat_path, 'w') as f:
        f.write(bat_content)
        
    added_to_path = ensure_in_path()
    if added_to_path:
        console.print(f"[success]Installed![/success] You may need to restart your terminal for 'agy-profiles' to work globally.")

def setup_wizard(config):
    console.print(Panel("[bold cyan]Welcome to Antigravity Profile Manager Setup[/bold cyan]\nLet's configure your default paths first."))
    
    # 1. IDE Path
    ide_path = config.get("ide_path", DEFAULT_EXE)
    if not os.path.exists(ide_path):
        console.print(f"[warning]Could not find Antigravity IDE at {ide_path}[/warning]")
        ide_path = Prompt.ask("Enter the absolute path to Antigravity.exe", default=ide_path)
    else:
        ans = Prompt.ask(f"Found Antigravity IDE at [green]{ide_path}[/green]. Press Enter to accept, or provide a new path", default=ide_path)
        ide_path = ans
        
    # 2. Desktop Destination
    dest_path = config.get("dest_path", DEFAULT_DESKTOP)
    dest_path = Prompt.ask(f"Where should shortcuts be created?", default=dest_path)
    
    config["ide_path"] = ide_path
    config["dest_path"] = dest_path
    save_config(config)
    
    console.print("[success]Setup complete! Configuration saved.[/success]\n")
    return config

def create_shortcut(profile_name, project_path, dest_dir, exe_path, shortcut_name=None):
    os.makedirs(dest_dir, exist_ok=True)
    
    if not shortcut_name:
        shortcut_name = profile_name
        
    shortcut_path = os.path.join(dest_dir, f"{shortcut_name}.lnk")
    user_data_dir = os.path.expandvars(rf"%LOCALAPPDATA%\AntigravityProfiles\{profile_name}")
    
    arguments = f'--user-data-dir="{user_data_dir}" "{project_path}"'
    
    ps_script = f'''
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
$Shortcut.TargetPath = "{exe_path}"
$Shortcut.Arguments = '{arguments}'
$Shortcut.Save()
'''
    try:
        subprocess.run(["powershell", "-Command", ps_script], check=True, capture_output=True, text=True)
        console.print(Panel(
            f"[bold green]Success![/bold green] Shortcut created for profile [cyan]{profile_name}[/cyan]\n"
            f"[dim]Path:[/dim] {shortcut_path}\n"
            f"[dim]Project:[/dim] {project_path}",
            title="Profile Created"
        ))
        return True
    except subprocess.CalledProcessError as e:
        console.print(f"[danger]Failed to create shortcut:[/danger] {e.stderr}")
        return False

def interactive_mode():
    config = load_config()
    console.clear()
    console.print(Panel("[bold magenta]Antigravity IDE Profile Manager[/bold magenta]", expand=False))
    
    if not config.get("ide_path"):
        config = setup_wizard(config)
        
    if not config.get("installed"):
        if Confirm.ask("Do you want to install 'agy-profiles' command to run this from anywhere?"):
            install_cli()
        config["installed"] = True
        save_config(config)
        
    while True:
        console.print("\n[bold]Create Profile Shortcuts[/bold] (or press Ctrl+C to exit)")
        
        base_name = Prompt.ask("Base Profile/Shortcut Name (e.g., 'User')")
        if not base_name:
            continue
            
        count_str = Prompt.ask("How many shortcuts to generate?", default="1")
        try:
            count = int(count_str)
            if count <= 0:
                raise ValueError
        except ValueError:
            console.print("[warning]Please enter a valid positive number.[/warning]")
            continue
            
        current_dir = os.getcwd()
        project_path = Prompt.ask("Project Path to open for these profiles", default=current_dir)
        project_path = project_path.strip("()\"' ")
        
        dest_dir = Prompt.ask("Destination folder for shortcuts", default=config.get("dest_path", DEFAULT_DESKTOP))
        dest_dir = dest_dir.strip("()\"' ")
        
        config["dest_path"] = dest_dir
        save_config(config)
        
        if count == 1:
            create_shortcut(
                profile_name=base_name,
                project_path=project_path,
                dest_dir=dest_dir,
                exe_path=config["ide_path"],
                shortcut_name=base_name
            )
        else:
            for i in range(1, count + 1):
                name = f"{base_name}{i}"
                create_shortcut(
                    profile_name=name,
                    project_path=project_path,
                    dest_dir=dest_dir,
                    exe_path=config["ide_path"],
                    shortcut_name=name
                )
        
        if not Confirm.ask("\nCreate more profiles?"):
            break

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Antigravity IDE Profile Manager")
    parser.add_argument("--reconfigure", action="store_true", help="Re-run the setup wizard")
    
    args = parser.parse_args()
    
    if args.reconfigure:
        setup_wizard(load_config())
    else:
        try:
            interactive_mode()
        except KeyboardInterrupt:
            console.print("\n[info]Exiting...[/info]")
            sys.exit(0)
