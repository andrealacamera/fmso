import os
import sys
import glob
from datetime import datetime, timedelta
from astropy.io import fits

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText

# Optional: Try to import sirilpy if running inside Siril environment
try:
    import sirilpy as siril

    SIRIL_AVAILABLE = True
except ImportError:
    SIRIL_AVAILABLE = False


class FitsOrganizerTk:
    def __init__(self, root):
        self.root = root
        self.root.title("FITS Midnight Session Organizer")
        self.root.geometry("650x540")
        self.root.minsize(550, 420)

        # Apply a clean theme if available
        style = ttk.Style()
        if "clam" in style.theme_names():
            style.theme_use("clam")

        self._build_ui()
        self._initialize_defaults()

    def _build_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Input Directory
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=4)
        ttk.Label(input_frame, text="Input Folder:", width=15, anchor="w").pack(side=tk.LEFT)
        self.input_entry = ttk.Entry(input_frame)
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(input_frame, text="Browse...", command=self.browse_input).pack(side=tk.RIGHT)

        # Output Directory
        output_frame = ttk.Frame(main_frame)
        output_frame.pack(fill=tk.X, pady=4)
        ttk.Label(output_frame, text="Output Folder:", width=15, anchor="w").pack(side=tk.LEFT)
        self.output_entry = ttk.Entry(output_frame)
        self.output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(output_frame, text="Browse...", command=self.browse_output).pack(side=tk.RIGHT)

        # Output Folder Prefix Entry
        folder_prefix_frame = ttk.Frame(main_frame)
        folder_prefix_frame.pack(fill=tk.X, pady=4)
        ttk.Label(folder_prefix_frame, text="Folder Prefix:", width=15, anchor="w").pack(side=tk.LEFT)
        self.folder_prefix_entry = ttk.Entry(folder_prefix_frame)
        self.folder_prefix_entry.insert(0, "Obs_")  # Default value
        self.folder_prefix_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # File Prefix Entry
        prefix_frame = ttk.Frame(main_frame)
        prefix_frame.pack(fill=tk.X, pady=4)
        ttk.Label(prefix_frame, text="File Prefix:", width=15, anchor="w").pack(side=tk.LEFT)
        self.prefix_entry = ttk.Entry(prefix_frame)
        self.prefix_entry.insert(0, "Light_")  # Default value
        self.prefix_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Action Buttons (Run and Cancel/Close)
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)

        self.run_btn = ttk.Button(button_frame, text="Organize FITS Files", command=self.process_files)
        self.run_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        self.cancel_btn = ttk.Button(button_frame, text="Cancel", command=self.root.destroy)
        self.cancel_btn.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))

        # Log Window
        ttk.Label(main_frame, text="Log Output:").pack(anchor="w")
        self.log_area = ScrolledText(main_frame, height=12, state="disabled", wrap=tk.WORD)
        self.log_area.pack(fill=tk.BOTH, expand=True, pady=2)

    def _initialize_defaults(self):
        # Determine working directory: Siril current working dir or OS current dir
        initial_dir = os.getcwd()
        if SIRIL_AVAILABLE:
            try:
                siril_app = siril.PySiril()
                siril_dir = siril_app.get_working_directory()
                if siril_dir and os.path.exists(siril_dir):
                    initial_dir = siril_dir
            except Exception:
                pass

        self.input_entry.insert(0, initial_dir)

    def browse_input(self):
        current_val = self.input_entry.get().strip()
        start_dir = current_val if os.path.exists(current_val) else os.getcwd()
        path = filedialog.askdirectory(title="Select Folder Containing FITS Files", initialdir=start_dir)
        if path:
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, path)

    def browse_output(self):
        current_val = self.output_entry.get().strip()
        start_dir = current_val if os.path.exists(current_val) else os.getcwd()
        path = filedialog.askdirectory(title="Select Target Output Directory", initialdir=start_dir)
        if path:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, path)

    def log(self, message):
        self.log_area.config(state="normal")
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)
        self.log_area.config(state="disabled")

    def get_observation_date(self, fits_path):
        with fits.open(fits_path) as hdul:
            header = hdul[0].header
            date_str = header.get("DATE-OBS") or header.get("DATE")
            if not date_str:
                return None

            obs_time = datetime.fromisoformat(date_str.replace("Z", ""))
            # 12-hour offset groups files across midnight (23:14, 23:55, 00:13) into the starting evening
            return (obs_time - timedelta(hours=12)).strftime("%Y-%m-%d")

    def process_files(self):
        # Clear log area
        self.log_area.config(state="normal")
        self.log_area.delete("1.0", tk.END)
        self.log_area.config(state="disabled")

        base_input = self.input_entry.get().strip()
        base_output = self.output_entry.get().strip()
        folder_prefix = self.folder_prefix_entry.get().strip()
        file_prefix = self.prefix_entry.get().strip()

        if not base_input or not base_output:
            messagebox.showerror("Missing Information", "Please select both Input and Output folders.")
            return

        if not os.path.exists(base_input):
            self.log(f"Error: Input folder does not exist: {base_input}")
            return

        # Read FITS directly from input directory
        fits_files = glob.glob(os.path.join(base_input, "*.fit*"))
        if not fits_files:
            self.log(f"No FITS files (.fit / .fits) found directly in: {base_input}")
            return

        self.log(f"Processing {len(fits_files)} FITS files...")
        self.log(f"Folder Prefix: '{folder_prefix}' | File Prefix: '{file_prefix}'\n")
        success_count = 0

        for file_path in fits_files:
            try:
                obs_date = self.get_observation_date(file_path)
                if not obs_date:
                    self.log(f"Skipped (No DATE-OBS header): {os.path.basename(file_path)}")
                    continue

                folder_name = f"{folder_prefix}{obs_date}"
                dest_folder = os.path.join(base_output, folder_name)
                os.makedirs(dest_folder, exist_ok=True)

                original_name = os.path.basename(file_path)

                # Apply file prefix to target symlink filename if not already present
                if file_prefix and not original_name.startswith(file_prefix):
                    target_name = f"{file_prefix}{original_name}"
                else:
                    target_name = original_name

                symlink_target = os.path.join(dest_folder, target_name)

                if not os.path.exists(symlink_target):
                    rel_src = os.path.relpath(file_path, dest_folder)
                    os.symlink(rel_src, symlink_target)
                    self.log(f"Linked: {original_name} ➔ {folder_name}/{target_name}")
                else:
                    self.log(f"Exists: {target_name} in {folder_name}/")

                success_count += 1

            except Exception as e:
                self.log(f"Error processing {os.path.basename(file_path)}: {e}")

        self.log(f"\nDone! Organized {success_count} files into '{base_output}'.")

        # Change button label to "Close" after successful run
        self.cancel_btn.config(text="Close")


if __name__ == "__main__":
    root = tk.Tk()
    app = FitsOrganizerTk(root)
    root.mainloop()
