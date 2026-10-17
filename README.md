# FITS Midnight Session Organizer 
## My first script for Siril

A Python/GUI tool for [Siril](https://siril.org/) that reads `.fit` / `.fits` files from a target directory, inspects the `DATE-OBS` metadata, and groups the files into observation folders by night, maintaining multi-night sessions across midnight. 

## Features

* **Midnight Session Handling**: Automatically shifts timestamps back by 12 hours so images taken across midnight (e.g., `23:14`, `23:55`, and `00:13`) are correctly assigned to the same starting evening date (`2026-09-11`).

* **Siril Working Directory Integration**: Pre-fills the **Input Folder** with Siril's active working directory automatically when launched inside Siril.

* **Custom Folder & File Filter Prefixes**: 
  * Custom folder prefix (default: `Obs_`) prepended to the date string (e.g., `Obs_YYYY-MM-DD`).
  * Filters input files in the chosen folder. Only FITS files starting with this prefix (default: `Light_`) will be processed and symlinked. (Leave blank to process all `.fits`/`.fit` files).

* **Symlink Creation**: Uses relative symbolic links to avoid duplicating heavy raw data files.

* **Original Filename Preservation:** The symlinks created inside the `Obs_YYYY-MM-DD` output folders retain their exact original filenames without adding additional prefixes.

* **Tkinter GUI**: Runs natively on standard Python without heavy extra dependencies like Qt/PySide. 

## Prerequisites & Requirements

This script requires Python 3.12+ and the following Python packages:

* **`astropy`** (required for FITS header reading)

* **`tkinter`** (included by default in standard Python distributions)

* **`sirilpy`** (optional, automatically used if launched directly within Siril as recommended)

### Installing Dependencies 

Open a terminal or command prompt and run:

```bash
pip install astropy
```

> **Windows Users**: Creating symbolic links (symlinks) requires either running your terminal/Siril as **Administrator** or enabling **Developer Mode** in Windows Settings (*Settings > Update & Security > For developers > Developer Mode*).

## Installation in Siril

To make this script accessible directly from the **Scripts** menu or executable via Siril's command interface:

1. Locate or create your local user script directory:

   * **Linux**: `~/.config/siril/scripts/` or `~/.local/share/siril/scripts/`

   * **macOS**: `~/Library/Application Support/org.siril.Siril/siril-scripts/`

   * **Windows**: `%APPDATA%\siril\scripts\`

   * **User Custom Directory**: You can also use any custom folder on your system by configuring it directly inside Siril under **Preferences** -> **Scripts** -> **Script Storage Directories** (or setting `scripts_user`).

2. Save the Python script (e.g., `fmso.py`) into your chosen script directory.

3. Open **Siril** and navigate to **Preferences** -> **Scripts**.

4. Ensure your folder is listed, then click **Refresh** (or restart Siril). The script should now appear under the user scripts menu.

## How to Use

### 1. **Launch the Script**:

#### Option A: From inside Siril (Recommended)

- Open Siril and set your working directory to the folder containing your FITS files.
- Go to the Scripts menu in the top bar **Scripts** -> **Python Scripts** -> **Scripts**.
- Select the FITS Midnight Session Organizer (i.e. `fmso.py`).

#### Option B: Standalone from Terminal / Command Prompt

If you prefer running the tool outside Siril:

- Open a terminal or command window.
- Run: `python fmso.py`

### 2. **Configure Settings**:

   * **Input Folder**: Pre-filled with your current Siril working directory. Select the folder containing your raw FITS files.

   * **Output Folder**: Select the destination directory where the session folders will be created.

   * **Folder Prefix**: Prefix for observation folders created in output directory (default: `Obs_`).

   * **File Filter Prefix:** (Optional) Enter a filename prefix to filter input files (defaults to `Light_`). Only FITS files starting with this prefix will be included.

3. **Run & Exit**:

   * Click **Organize FITS Files**.

   * Monitor progress in the **Log Output** panel.

   * Once execution completes, click **Close** (or click **Cancel** at any time prior to exit).

## Output Directory Structure

Given an input directory with files captured across the midnight boundary on September 11th into September 12th:

```text
Output_Directory/
└── Obs_2026-09-11/
    ├── Light_frame_2314.fits -> ../Input/Light_frame_2314.fits
    ├── Light_frame_2355.fits -> ../Input/Light_frame_2355.fits
    ├── (skipped) -> ../Input/Magnitude_frame_2359.fits
    └── Light_frame_0013.fits -> ../Input/Light_frame_0013.fits

```

## Author

Andrea La Camera [TEIGA](https://teiga.it).

## License

MIT License. Free to use, modify, and distribute.

## Updated

Last update 2026-10-17