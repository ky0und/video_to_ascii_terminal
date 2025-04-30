# Video to ASCII Art Player

A Python script that converts video files into ASCII art and plays them back directly in your terminal/console window. Optimized for speed using NumPy and OpenCV.

![Demo GIF](https://github.com/ky0und/video_to_ascii_terminal/demo.gif)

## Features

*   Plays standard video files (formats supported by OpenCV) as ASCII art.
*   Adjustable output "resolution" via a modifier factor (`-r`) to control detail vs. performance/size.
*   Attempts to match the original video's frame rate.
*   **Windows Specific:** Automatically adjusts console font size and dimensions for optimal viewing based on the resolution modifier.
*   Uses efficient NumPy vectorized operations for fast grayscale-to-ASCII character mapping.
*   Customizable ASCII character ramp within the script (`ASCII_CHARS`) for different visual styles.

## Requirements

*   **Python:** 3.7+ recommended
*   **Libraries:**
    *   `opencv-python`
    *   `numpy`
*   **Operating System:**
    *   **Windows:** Full functionality, including automatic console font and size adjustments.
    *   **Linux/macOS:** The script *may* run, but the console font/size adjustment using `ctypes` will fail (a warning will be printed). You will need to manually resize your terminal and ensure you're using a monospaced font for best results.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/your-repo-name.git
    cd your-repo-name
    ```

2.  **Install the required Python libraries:**
    ```bash
    pip install opencv-python numpy
    ```

## Usage

Run the script from your terminal, providing the path to the video file as the main argument.

```bash
python video_to_ascii.py path/to/your/video.mp4
```
To adjust size/detail use the -r or --res_mod flag. A higher number means the video dimensions are divided by a larger factor, resulting in a smaller ASCII output (less detail, potentially faster). The default is 2.

### Smaller output (divides width/height by 4)
```bash
python video_to_ascii.py video.avi -r 4
```

### Larger output (divides width/height by 1 - uses original resolution, may be slow/too large)
```bash
python video_to_ascii.py movie.mkv -r 1
```

### Specifying Console Font (Windows Only):

Use the -f or --font flag to suggest a console font. Use monospaced fonts like Consolas, Courier New, etc.

```bash
python video_to_ascii.py my_clip.webm -r 2 -f "Courier New"
```

### Stopping Playback:
Press Ctrl + C in the terminal to stop the script.

## Command-Line Arguments

**video_path** - (Required): Positional argument for the path to the input video file.

**-r**, **--res_mod** - (Optional): Integer resolution modifier. Divides video width and height by this factor. Defaults to 2. Affects output size, detail, and console font size heuristic (on Windows).

**-f**, **--font** - (Optional): String specifying the desired console font name (e.g., "Consolas", "Courier New"). Primarily affects Windows console setup. Defaults to "Consolas".

**--speed** - (Optional): Playback speed multiplier (e.g., 1.0 is normal, 2.0 is 2x speed).
#License

CC0 1.0 Universal

