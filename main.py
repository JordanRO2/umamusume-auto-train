from utils.tools import sleep
import pygetwindow as gw
import threading
import uvicorn
import keyboard
import pyautogui
import time
import sys

import utils.constants as constants
from utils.log import info, warning, error, debug

from core.execute import career_lobby
import core.state as state
from server.main import app
from update_config import update_config
from utils.debug_mode import enable_debug_mode, disable_debug_mode

hotkey = "f1"
debug_hotkey = "f2"  # Toggle debug mode
step_hotkey = "f3"   # Toggle step-by-step mode
editor_hotkey = "f4"  # Open region editor

def focus_umamusume():
  try:
    win = gw.getWindowsWithTitle("Umamusume")
    target_window = next((w for w in win if w.title.strip() == "Umamusume"), None)
    if not target_window:
      if not state.WINDOW_NAME:
        error("Window name cannot be empty! Please set window name in the config.")
        return False
      info(f"Couldn't get the steam version window, trying {state.WINDOW_NAME}.")
      win = gw.getWindowsWithTitle(state.WINDOW_NAME)
      target_window = next((w for w in win if w.title.strip() == state.WINDOW_NAME), None)
      if not target_window:
        error(f"Couldn't find target window named \"{state.WINDOW_NAME}\". Please double check your window name config.")
        return False

      constants.adjust_constants_x_coords()
      if target_window.isMinimized:
        target_window.restore()
      else:
        target_window.minimize()
        sleep(0.2)
        target_window.restore()
        sleep(0.5)
      pyautogui.press("esc")
      pyautogui.press("f11")
      time.sleep(5)
      close_btn = pyautogui.locateCenterOnScreen("assets/buttons/bluestacks/close_btn.png", confidence=0.8, minSearchTime=2)
      if close_btn:
        pyautogui.click(close_btn)
      return True

    if target_window.isMinimized:
      target_window.restore()
    else:
      target_window.minimize()
      sleep(0.2)
      target_window.restore()
      sleep(0.5)
  except Exception as e:
    error(f"Error focusing window: {e}")
    return False
  return True

def main():
  print("Uma Auto!")

  # Check for debug mode arguments
  if "--debug" in sys.argv or "-d" in sys.argv:
    enable_debug_mode(show_zones=True, step_mode=False)
    info("Debug mode enabled via command line")
  if "--step" in sys.argv or "-s" in sys.argv:
    enable_debug_mode(show_zones=True, step_mode=True)
    info("Step-by-step debug mode enabled via command line")

  try:
    state.reload_config()
    state.stop_event.clear()

    if focus_umamusume():
      info(f"Config: {state.CONFIG_NAME}")
      info("Press F2 for debug, F3 for step mode, F4 for region editor")
      career_lobby()
    else:
      error("Failed to focus Umamusume window")
  except Exception as e:
    error(f"Error in main thread: {e}")
  finally:
    disable_debug_mode()
    debug("[BOT] Stopped.")

def toggle_debug_mode():
  """Toggle debug mode on/off"""
  from utils.debug_mode import DEBUG_MODE
  if DEBUG_MODE:
    disable_debug_mode()
    info("[DEBUG] Debug mode disabled")
  else:
    enable_debug_mode(show_zones=True, step_mode=False)
    info("[DEBUG] Debug mode enabled (F3 for step-by-step)")

def toggle_step_mode():
  """Toggle step-by-step mode on/off"""
  from utils.debug_mode import DEBUG_MODE, STEP_BY_STEP
  if not DEBUG_MODE:
    enable_debug_mode(show_zones=True, step_mode=True)
    info("[DEBUG] Step-by-step mode enabled")
  else:
    if STEP_BY_STEP:
      enable_debug_mode(show_zones=True, step_mode=False)
      info("[DEBUG] Step-by-step mode disabled, debug still active")
    else:
      enable_debug_mode(show_zones=True, step_mode=True)
      info("[DEBUG] Step-by-step mode enabled")

def open_region_editor():
  """Open the interactive region editor"""
  from utils.simple_region_editor import SimpleTransparentEditor
  info("[EDITOR] Opening TRANSPARENT overlay editor...")
  info("[EDITOR] You can see and edit regions over the live game!")
  info("[EDITOR] Controls: 'n'=new, 't'=transparency, 's'=save, ESC=exit")

  # Note: Bot continues running with overlay
  editor = SimpleTransparentEditor()
  editor.run()

  info("[EDITOR] Transparent overlay closed")

def hotkey_listener():
  # Register debug hotkeys
  keyboard.add_hotkey(debug_hotkey, toggle_debug_mode)
  keyboard.add_hotkey(step_hotkey, toggle_step_mode)
  keyboard.add_hotkey(editor_hotkey, open_region_editor)

  while True:
    keyboard.wait(hotkey)
    with state.bot_lock:
      if state.is_bot_running:
        debug("[BOT] Stopping...")
        state.stop_event.set()
        state.is_bot_running = False

        if state.bot_thread and state.bot_thread.is_alive():
          debug("[BOT] Waiting for bot to stop...")
          state.bot_thread.join(timeout=3)

          if state.bot_thread.is_alive():
            debug("[BOT] Bot still running, please wait...")
          else:
            debug("[BOT] Bot stopped completely")

        state.bot_thread = None
      else:
        debug("[BOT] Starting...")
        state.is_bot_running = True
        state.bot_thread = threading.Thread(target=main, daemon=True)
        state.bot_thread.start()
    sleep(0.5)

def start_server():
  res = pyautogui.resolution()
  if res.width != 1920 or res.height != 1080:
    error(f"Your resolution is {res.width} x {res.height}. Please set your screen to 1920 x 1080.")
    return
  host = "127.0.0.1"
  port = 8000
  info(f"Press '{hotkey}' to start/stop the bot.")
  print(f"[SERVER] Open http://{host}:{port} to configure the bot.")
  config = uvicorn.Config(app, host=host, port=port, workers=1, log_level="warning")
  server = uvicorn.Server(config)
  server.run()

if __name__ == "__main__":
  update_config()
  threading.Thread(target=hotkey_listener, daemon=True).start()
  start_server()
