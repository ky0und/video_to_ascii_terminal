import cv2
import numpy as np
import os
import ctypes
import sys
import time
import argparse

LF_FACESIZE = 32
STD_OUTPUT_HANDLE = -11

class COORD(ctypes.Structure):
    _fields_ = [("X", ctypes.c_short), ("Y", ctypes.c_short)]

class CONSOLE_FONT_INFOEX(ctypes.Structure):
    _fields_ = [("cbSize", ctypes.c_ulong),
                ("nFont", ctypes.c_ulong),
                ("dwFontSize", COORD),
                ("FontFamily", ctypes.c_uint),
                ("FontWeight", ctypes.c_uint),
                ("FaceName", ctypes.c_wchar * LF_FACESIZE)]

ASCII_CHARS = "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^`'. "
ASCII_CHARS = ASCII_CHARS[::-1]
ASCII_MAP_LEN = len(ASCII_CHARS)
ASCII_MAP_INDICES = np.arange(ASCII_MAP_LEN)

GRAY_TO_INDEX = np.clip(
    np.round(np.linspace(0, ASCII_MAP_LEN - 1, 256)).astype(int),
    0,
    ASCII_MAP_LEN - 1
)
ASCII_LOOKUP = np.array(list(ASCII_CHARS))[GRAY_TO_INDEX]


def setup_console(width: int, height: int, res_mod: int, font_name: str):
    """
    Configures the Windows console size and font.
    (Keep this function largely the same as the previous refactoring)
    """
    font_size_map = {1: 2, 2: 6, 3: 11, 4: 15, 5: 19}
    font_size = font_size_map.get(res_mod, 6)

    font = CONSOLE_FONT_INFOEX()
    font.cbSize = ctypes.sizeof(CONSOLE_FONT_INFOEX)
    font.nFont = 12
    font.dwFontSize.X = font_size
    font.dwFontSize.Y = font_size
    font.FontFamily = 54  # FF_MODERN | FIXED_PITCH
    font.FontWeight = 400 # FW_NORMAL
    try:
        font.FaceName = font_name[:LF_FACESIZE-1]
    except Exception:
        print(f"Warning: Could not set font name '{font_name}'. Using default.", file=sys.stderr)
        font.FaceName = "Consolas"

    try:
        handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
        if handle and handle != -1: 
             ctypes.windll.kernel32.SetCurrentConsoleFontEx(
                 handle, ctypes.c_long(False), ctypes.pointer(font))
        else:
             print("Warning: Could not get standard output handle.", file=sys.stderr)

    except OSError as e:
         print(f"Warning: Failed to set console font (OS Error). Error: {e}", file=sys.stderr)
    except Exception as e:
        print(f"Warning: Failed to set console font (Unknown Error). Error: {e}", file=sys.stderr)

    try:
        os.system(f'mode con: cols={width} lines={height}')
    except Exception as e:
        print(f"Warning: Failed to set console size. Error: {e}", file=sys.stderr)

def clear_console():
    """Clears the console screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

# Using INTER_NEAREST might be slightly faster than INTER_AREA but lower quality
RESIZE_INTERPOLATION = cv2.INTER_AREA

def create_ascii_frame_fast(frame: np.ndarray, target_width: int, target_height: int) -> str:
    """
    Converts a frame to ASCII using optimized OpenCV and NumPy.
    """
    try:
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        resized_frame = cv2.resize(gray_frame,
                                   (target_width, target_height),
                                   interpolation=RESIZE_INTERPOLATION)

        char_frame = ASCII_LOOKUP[resized_frame]

        return "\n".join("".join(row) for row in char_frame)

          # Return empty string on error
    except cv2.error as e:
        return "" 
    except IndexError:
        return "" 
    except Exception as e:
        return ""

def main():
    parser = argparse.ArgumentParser(description="Fast video to ASCII art conversion for the console.")
    parser.add_argument("video_path", help="Path to the input video file.")
    parser.add_argument("-r", "--res_mod", type=int, default=2,
                        help="Resolution modifier (default: 2). Higher value = smaller output/faster processing.")
    parser.add_argument("-f", "--font", type=str, default="Consolas",
                        help="Console font name (default: Consolas). Use monospaced fonts.")
    parser.add_argument("--speed", type=float, default=1.0, help="Playback speed multiplier (e.g., 1.0 is normal, 2.0 is 2x speed).")

    args = parser.parse_args()

    if not os.path.exists(args.video_path):
        print(f"Error: Video file not found: '{args.video_path}'", file=sys.stderr)
        sys.exit(1)

    if args.res_mod <= 0:
        print("Error: Resolution modifier must be positive.", file=sys.stderr)
        sys.exit(1)

    vidcap = cv2.VideoCapture(args.video_path)
    if not vidcap.isOpened():
        print(f"Error: Cannot open video file: '{args.video_path}'", file=sys.stderr)
        sys.exit(1)

    try:
        fps = vidcap.get(cv2.CAP_PROP_FPS)
        frame_width = int(vidcap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(vidcap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        if fps <= 0:
            print("Warning: Invalid FPS detected ({fps}), defaulting to 30 FPS.", file=sys.stderr)
            fps = 30.0
        if frame_width <= 0 or frame_height <= 0:
            raise ValueError("Invalid video dimensions.")

    except Exception as e:
        print(f"Error reading video properties: {e}", file=sys.stderr)
        vidcap.release()
        sys.exit(1)

    frame_duration = 1.0 / fps
    frame_duration /= args.speed

    target_width = max(1, frame_width // args.res_mod)
    target_height = max(1, frame_height // args.res_mod)

    if os.name == 'nt':
        setup_console(target_width, target_height, args.res_mod, args.font)
    else:
        print("Warning: Console font/size setup skipped (Windows only).", file=sys.stderr)
        print(f"Target dimensions: {target_width}x{target_height}. Resize terminal manually if needed.")

    try:
        frame_count = 0
        loop_start_time = time.perf_counter()

        while True:
            success, frame = vidcap.read()
            if not success:
                break # End of video or error

            ascii_art = create_ascii_frame_fast(frame, target_width, target_height)

            clear_console()

            sys.stdout.write(ascii_art + '\r')
            sys.stdout.flush() # Ensure output is displayed immediately

            frame_count += 1

            current_time = time.perf_counter()
            elapsed_since_last_loop = current_time - loop_start_time

            sleep_time = frame_duration - elapsed_since_last_loop

            if sleep_time > 0:
                time.sleep(sleep_time)

            # Update start time for the next loop iteration precisely after sleep/work
            loop_start_time = time.perf_counter()


    except KeyboardInterrupt:
        print("\nPlayback interrupted.")
    finally:
        vidcap.release()
        print(f"\nVideo released. Processed ~{frame_count} frames.")
        clear_console()

if __name__ == "__main__":
    main()