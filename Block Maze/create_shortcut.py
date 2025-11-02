import os
import sys
import ctypes
from ctypes import wintypes
import pythoncom
from win32com.shell import shell, shellcon

def create_shortcut(target_path, shortcut_name, icon_path, description=""):
    """
    Create a Windows shortcut (.lnk) file
    
    Args:
        target_path (str): Path to the target file to be executed
        shortcut_name (str): Name of the shortcut (without .lnk extension)
        icon_path (str): Path to the icon file (.ico or .png)
        description (str): Description of the shortcut
    """
    # Get the Desktop path
    desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    shortcut_path = os.path.join(desktop, f"{shortcut_name}.lnk")
    
    # Create shortcut
    shortcut = pythoncom.CoCreateInstance(
        shell.CLSID_ShellLink, None,
        pythoncom.CLSCTX_INPROC_SERVER, shell.IID_IShellLink
    )
    
    # Set shortcut properties
    shortcut.SetPath(target_path)
    shortcut.SetWorkingDirectory(os.path.dirname(target_path))
    shortcut.SetDescription(description)
    
    # Set the icon
    shortcut.SetIconLocation(icon_path, 0)
    
    # Save the shortcut
    persist_file = shortcut.QueryInterface(pythoncom.IID_IPersistFile)
    persist_file.Save(shortcut_path, 0)
    
    return shortcut_path

def main():
    # Define paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    target_path = os.path.join(current_dir, "juego.py")
    icon_path = os.path.join(current_dir, "assets", "player", "CRISTAL.png")
    
    # Convert PNG to ICO if needed
    try:
        from PIL import Image
        ico_path = os.path.join(os.path.dirname(icon_path), "CRISTAL.ico")
        if not os.path.exists(ico_path):
            img = Image.open(icon_path)
            img.save(ico_path, format='ICO')
        icon_path = ico_path
    except Exception as e:
        print(f"Warning: Could not convert PNG to ICO: {e}")
    
    # Create the shortcut
    try:
        shortcut = create_shortcut(
            target_path=sys.executable,  # Python executable
            shortcut_name="Block Maze",
            icon_path=icon_path,
            description="Block Maze Game"
        )
        print(f"Shortcut created successfully at: {shortcut}")
    except Exception as e:
        print(f"Error creating shortcut: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    # Check if running as administrator
    try:
        if ctypes.windll.shell32.IsUserAnAdmin() == 0:
            print("This script requires administrator privileges. Please run as administrator.")
            input("Press Enter to exit...")
            sys.exit(1)
    except:
        pass  # If we can't check, try to continue anyway
    
    main()
