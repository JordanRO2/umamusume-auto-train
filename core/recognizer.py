import cv2
import numpy as np
from PIL import ImageGrab, ImageStat

from utils.log import info, warning, error, debug
from utils.screenshot import capture_region
from utils.debug_mode import (
    DEBUG_MODE, show_debug_info, draw_search_zone,
    log_search_attempt, wait_for_step
)
from pathlib import Path

def match_template(template_path, region=None, threshold=0.85):
  # Debug: Show what we're searching for
  if DEBUG_MODE:
    from utils.debug_mode import log_message, save_debug_screenshot
    log_message(f"match_template called: {template_path}, region={region}, threshold={threshold}")
    show_debug_info(template_path=template_path, region=region, threshold=threshold)

  # Get screenshot
  if region:
    screen = np.array(ImageGrab.grab(bbox=region))  # (left, top, right, bottom)
  else:
    screen = np.array(ImageGrab.grab())
  screen_bgr = cv2.cvtColor(screen, cv2.COLOR_RGB2BGR)

  # Debug: Save search region to file instead of blocking display
  if DEBUG_MODE:
    from utils.debug_mode import save_debug_screenshot
    debug_image = screen_bgr.copy()
    if region:
      cv2.rectangle(debug_image, (0, 0), (debug_image.shape[1]-1, debug_image.shape[0]-1), (0, 255, 0), 3)
      cv2.putText(debug_image, f"Search: {template_path}", (10, 30),
                 cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    save_debug_screenshot(debug_image, f"search_{Path(template_path).stem}")

  # Load template
  template = cv2.imread(template_path, cv2.IMREAD_COLOR)  # safe default
  if template.shape[2] == 4:
    template = cv2.cvtColor(template, cv2.COLOR_BGRA2BGR)
  result = cv2.matchTemplate(screen_bgr, template, cv2.TM_CCOEFF_NORMED)
  loc = np.where(result >= threshold)

  h, w = template.shape[:2]
  boxes = [(x, y, w, h) for (x, y) in zip(*loc[::-1])]

  filtered_boxes = deduplicate_boxes(boxes)

  # Debug: Log and save matches found
  if DEBUG_MODE:
    from utils.debug_mode import log_message, save_debug_screenshot
    log_message(f"Found {len(filtered_boxes)} matches (before dedup: {len(boxes)})")

    if len(filtered_boxes) > 0:
      # Draw matches on debug image and save
      result_image = screen_bgr.copy()
      for x, y, w, h in filtered_boxes:
        cv2.rectangle(result_image, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.putText(result_image, "MATCH", (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
      save_debug_screenshot(result_image, f"found_{Path(template_path).stem}")

    # Log the search attempt
    log_search_attempt(f"match_template: {template_path}", region, len(filtered_boxes) > 0,
                      f"Found {len(filtered_boxes)} matches")

    # Wait for user to continue in step-by-step mode
    wait_for_step()

  return filtered_boxes

def multi_match_templates(templates, screen=None, threshold=0.85):
  if DEBUG_MODE:
    debug(f"Starting multi-template match for {len(templates)} templates")
    show_debug_info(threshold=threshold)

  if screen is None:
    screen = ImageGrab.grab()
  screen_bgr = cv2.cvtColor(np.array(screen), cv2.COLOR_RGB2BGR)

  # Debug: Log multi-search start
  if DEBUG_MODE:
    from utils.debug_mode import log_message, save_debug_screenshot
    debug_image = screen_bgr.copy()
    cv2.putText(debug_image, f"Multi-search: {list(templates.keys())}", (10, 30),
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
    save_debug_screenshot(debug_image, "multi_search_start")

  results = {}
  for name, path in templates.items():
    if DEBUG_MODE:
      debug(f"Searching for template: {name} -> {path}")

    template = cv2.imread(path, cv2.IMREAD_COLOR)
    if template is None:
      results[name] = []
      if DEBUG_MODE:
        warning(f"Template not found: {path}")
      continue
    if template.shape[2] == 4:
      template = cv2.cvtColor(template, cv2.COLOR_BGRA2BGR)

    result = cv2.matchTemplate(screen_bgr, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(result >= threshold)
    h, w = template.shape[:2]
    boxes = [(x, y, w, h) for (x, y) in zip(*loc[::-1])]
    results[name] = boxes

    # Debug: Log each template result
    if DEBUG_MODE:
      debug(f"  {name}: {len(boxes)} matches found")
      if len(boxes) > 0:
        # Draw this template's matches
        for x, y, w, h in boxes[:5]:  # Show max 5 matches
          cv2.rectangle(debug_image, (x, y), (x+w, y+h), (0, 255, 0), 2)
          cv2.putText(debug_image, name, (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
      log_search_attempt(f"multi_match: {name}", None, len(boxes) > 0, f"{len(boxes)} matches")

  # Debug: Save all matches combined
  if DEBUG_MODE:
    from utils.debug_mode import log_message, save_debug_screenshot
    total_matches = sum(len(boxes) for boxes in results.values())
    log_message(f"Total matches across all templates: {total_matches}")
    if total_matches > 0:
      save_debug_screenshot(debug_image, "multi_search_results")
    wait_for_step()

  return results

def deduplicate_boxes(boxes, min_dist=5):
  filtered = []
  for x, y, w, h in boxes:
    cx, cy = x + w // 2, y + h // 2
    if all(abs(cx - (fx + fw // 2)) > min_dist or abs(cy - (fy + fh // 2)) > min_dist
        for fx, fy, fw, fh in filtered):
      filtered.append((x, y, w, h))
  return filtered

def is_btn_active(region, treshold = 150):
  screenshot = capture_region(region)
  grayscale = screenshot.convert("L")
  stat = ImageStat.Stat(grayscale)
  avg_brightness = stat.mean[0]

  # Treshold btn
  return avg_brightness > treshold

def count_pixels_of_color(color_rgb=[117,117,117], region=None, tolerance=2):
    # [117,117,117] is gray for missing energy, we go 2 below and 2 above so that it's more stable in recognition
    if region:
        screen = np.array(ImageGrab.grab(bbox=region))  # (left, top, right, bottom)
    else:
        return -1

    color = np.array(color_rgb, np.uint8)

    # define min/max range ±2
    color_min = np.clip(color - tolerance, 0, 255)
    color_max = np.clip(color + tolerance, 0, 255)

    dst = cv2.inRange(screen, color_min, color_max)
    pixel_count = cv2.countNonZero(dst)
    return pixel_count

def find_color_of_pixel(region=None):
  if region:
    #we can only return one pixel's color here, so we take the x, y and add 1 to them
    region = (region[0], region[1], region[0]+1, region[1]+1)
    screen = np.array(ImageGrab.grab(bbox=region))  # (left, top, right, bottom)
    return screen[0]
  else:
    return -1

def closest_color(color_dict, target_color):
    closest_name = None
    min_dist = float('inf')
    target_color = np.array(target_color)
    for name, col in color_dict.items():
        col = np.array(col)
        dist = np.linalg.norm(target_color - col)  # Euclidean distance
        if dist < min_dist:
            min_dist = dist
            closest_name = name
    return closest_name
