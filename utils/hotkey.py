import pyautogui

def execute_hotkey(hotkey_str: str, interval: float = 0.1) -> bool:
    """
    Execute a hotkey combination using pyautogui.
    
    Args:
        hotkey_str: Hotkey string, e.g., "ctrl+c", "alt+tab", "win+r".
                    Keys should be separated by '+'.
        interval: Interval between key presses in seconds.
        
    Returns:
        bool: True if execution was successful, False otherwise.
    """
    if not hotkey_str:
        print("Error: Empty hotkey string provided.")
        return False
        
    try:
        # Split the hotkey string by '+' and strip whitespace
        keys = [key.strip().lower() for key in hotkey_str.split('+')]
        
        # pyautogui handles most key names directly.
        # Some adjustments might be needed for specific keys if they don't match standard names.
        # Common mappings: 'win' -> 'winleft' (usually safer on Windows)
        keys = ['winleft' if k == 'win' else k for k in keys]
        
        pyautogui.hotkey(*keys, interval=interval)
        return True
        
    except Exception as e:
        print(f"Error executing hotkey '{hotkey_str}': {e}")
        return False

if __name__ == "__main__":
    # Simple test to verify the function runs without error
    # We won't run disruptive hotkeys in the test
    print("Testing execute_hotkey function...")
    
    # Test with a harmless key press (e.g., just pressing 'ctrl' or similar, or just checking the function call)
    execute_hotkey("ctrl+alt+left") 
    pass
