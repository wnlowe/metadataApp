import customtkinter as ctk
from tkinterdnd2 import DND_FILES, TkinterDnD
import os
import tkinter as tk
import tkinter.messagebox
from datetime import datetime # Added this global import as it's used in get_current_time

global currentDir
currentDir = os.path.dirname(__file__)


class DragDropApp:
    def __init__(self):
        # Create the main window with TkinterDnD support
        self.root = TkinterDnD.Tk()
        self.root.title("Metadata Processor")
        self.root.geometry("600x1000")
        self.root.configure(bg="#2B2B2B") 
        self.root.protocol("WM_DELETE_WINDOW", self.on_app_close)
        # Set CustomTkinter appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")
        
        self.files = []
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ctk.CTkFrame(self.root, border_color="green")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title label
        title_label = ctk.CTkLabel(
            main_frame, 
            text="Metadata Processor", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(20, 15))
        
        # Create a regular tkinter frame for drag-and-drop (this is key!)
        # CustomTkinter frames don't work well with tkinterdnd2
        drop_container = ctk.CTkFrame(main_frame, height=220)
        drop_container.pack(fill="x", padx=20, pady=10)
        drop_container.pack_propagate(False)
        
        # Use a regular tkinter frame inside the CTk frame for DnD
        self.drop_frame = tk.Frame(
            drop_container,
            bg="#2b2b2b",  # Match dark theme
            relief="solid",
            bd=2,
            highlightbackground="gray",
            highlightthickness=2
        )
        self.drop_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Drop zone label
        self.drop_label = tk.Label(
            self.drop_frame,
            text="📁\n\nDrag & Drop Files Here\n(or click to browse)",
            font=("Arial", 14),
            bg="#2b2b2b",
            fg="gray",
            justify="center"
        )
        self.drop_label.pack(expand=True)
        
        # Configure drag and drop on the tkinter frame
        self.drop_frame.drop_target_register(DND_FILES)
        self.drop_frame.dnd_bind('<<Drop>>', self.on_drop)
        
        # Bind hover effects
        self.drop_frame.bind('<Enter>', self.on_drag_enter)
        self.drop_frame.bind('<Leave>', self.on_drag_leave)
        
        # Make clickable for file dialog
        self.drop_frame.bind("<Button-1>", self.browse_files)
        self.drop_label.bind("<Button-1>", self.browse_files)
        
        # Status label
        self.status_label = ctk.CTkLabel(
            main_frame,
            text="Ready to receive files...",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(pady=5)
        
        # File list section
        list_frame = ctk.CTkFrame(main_frame)
        list_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        list_title = ctk.CTkLabel(
            list_frame, 
            text="Selected Files:", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        list_title.pack(anchor="w", padx=15, pady=(15, 5))
        
        # Scrollable frame for file list
        self.file_list_frame = ctk.CTkScrollableFrame(
            list_frame, 
            height=120,
            corner_radius=10
        )
        self.file_list_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Button frame with more options
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # Left side buttons
        left_buttons = ctk.CTkFrame(button_frame, fg_color="transparent")
        left_buttons.pack(side="left", fill="x", expand=True)
        
        # Right side buttons
        right_buttons = ctk.CTkFrame(button_frame, fg_color="transparent")
        right_buttons.pack(side="right")
        
        # --- MODIFIED CODE START ---
        # Clear button (now on left)
        self.clear_button = ctk.CTkButton(
            left_buttons,
            text="🗑️ Clear All",
            command=self.clear_files,
            fg_color="#dc3545",
            hover_color="#c82333",
            height=35,
            width=100
        )
        self.clear_button.pack(side="left", padx=(15, 5), pady=10) # Packed left, with initial left padding
        
        # Open folder button (stays on left, after Clear All)
        self.open_folder_button = ctk.CTkButton(
            left_buttons,
            text="📁 Open Folder",
            command=self.open_containing_folder,
            fg_color="#6c757d",
            hover_color="#5a6268",
            height=35,
            width=120
        )
        self.open_folder_button.pack(side="left", padx=5, pady=10) # Packed left, next to Clear All
        
        # File count and size label (stays on right, left aligned within right_buttons)
        self.count_label = ctk.CTkLabel(
            right_buttons,
            text="Files: 0 | Size: 0 B",
            font=ctk.CTkFont(size=12)
        )
        self.count_label.pack(side="left", padx=(0, 15), pady=10) # Adjusted padx if needed, but keeping it concise
        
        # Export list button (now on right, after count label)
        self.export_button = ctk.CTkButton(
            right_buttons,
            text="📋 Export List",
            command=self.export_file_list,
            fg_color="#17a2b8",
            hover_color="#138496",
            height=35,
            width=120
        )
        self.export_button.pack(side="right", padx=15, pady=10) # Packed right, with right padding
        # --- MODIFIED CODE END ---
    
    def on_app_close(self):
        """
        Callback function executed when the user tries to close the window.
        You can perform cleanup or ask for confirmation here.
        """
        with open(currentDir + "\\src\\files.txt", "w", newline="") as f:
            for file in self.files:
                f.write(file + "\n")
        
        # if tkinter.messagebox.askokcancel("Exit Application", "Do you really want to exit?"):
            # Perform any cleanup actions here if necessary
            # e.g., saving settings, closing connections, stopping threads

        self.root.destroy() # This closes the window and exits the application
    # --------------------------------------------------         
    def on_drag_enter(self, event):
        """Visual feedback when dragging over drop zone"""
        self.drop_frame.configure(bg="#404040", highlightbackground="#9f005e")
        self.drop_label.configure(bg="#404040", fg="#9f005e")
        
    def on_drag_leave(self, event):
        """Reset visual feedback when leaving drop zone"""
        self.drop_frame.configure(bg="#2b2b2b", highlightbackground="gray")
        self.drop_label.configure(bg="#2b2b2b", fg="gray")
        
    def on_drop(self, event):
        """Handle dropped files with improved error handling and processing and file type restrictions"""
        # --- START OF ADDED CODE FOR FILE RESTRICTIONS ---
        allowed_extensions = ('.wav', '.csv', '.tsv', '.xls', '.xlsx')
        # --- END OF ADDED CODE FOR FILE RESTRICTIONS ---

        try:
            # Get the file paths from the drop event
            raw_data = event.data
            file_paths = self.root.tk.splitlist(raw_data)
            
            if not file_paths:
                self.status_label.configure(text="No files detected in drop.")
                # --- START OF ADDED CODE FOR FILE RESTRICTIONS ---
                self.reset_drop_zone() # Reset appearance if no files were dropped
                # --- END OF ADDED CODE FOR FILE RESTRICTIONS ---
                return
            
            # Update status and show processing
            self.status_label.configure(text=f"Processing {len(file_paths)} item(s)...")
            self.root.update_idletasks()  # Force UI update
            
            # Visual feedback
            self.drop_frame.configure(bg="#28a745", highlightbackground="#28a745")
            self.drop_label.configure(
                text="✅\n\nProcessing Files...\n" + f"({len(file_paths)} items)",
                bg="#28a745",
                fg="white"
            )
            
            # Process files with better path handling
            added_count = 0
            skipped_count = 0
            error_count = 0
            # --- START OF ADDED CODE FOR FILE RESTRICTIONS ---
            rejected_files_by_type = [] # To store names of files with wrong type
            # --- END OF ADDED CODE FOR FILE RESTRICTIONS ---
            
            for raw_path in file_paths:
                try:
                    # Handle different path formats and clean up
                    clean_path = raw_path.strip().strip('{}').strip('"').strip("'")
                    
                    # Skip if empty after cleaning
                    if not clean_path:
                        continue
                        
                    # Check if it's a file (not directory) and exists
                    if os.path.isfile(clean_path):
                        # --- START OF ADDED CODE FOR FILE RESTRICTIONS ---
                        file_ext = os.path.splitext(clean_path)[1].lower()
                        if file_ext not in allowed_extensions:
                            rejected_files_by_type.append(os.path.basename(clean_path))
                            error_count += 1 # Count as an error for overall status
                            self.status_label.configure(text=f"Rejected: {os.path.basename(clean_path)} (unsupported type)")
                            continue # Skip to next file if type is not allowed
                        # --- END OF ADDED CODE FOR FILE RESTRICTIONS ---

                        if clean_path not in self.files:
                            # Check file size (skip very large files > 1GB)
                            file_size = os.path.getsize(clean_path)
                            if file_size > 1024 * 1024 * 1024:  # 1GB limit
                                self.status_label.configure(text=f"Skipped large file: {os.path.basename(clean_path)}")
                                skipped_count += 1
                                continue
                                
                            self.files.append(clean_path)
                            self.add_file_to_list(clean_path)
                            added_count += 1
                        else:
                            skipped_count += 1
                    elif os.path.isdir(clean_path):
                        # Handle directory drops by adding all files in it
                        # --- START OF MODIFIED CODE FOR FILE RESTRICTIONS IN DIRECTORY ---
                        dir_files_added = self.process_directory(clean_path, allowed_extensions) # Pass allowed_extensions
                        added_count += dir_files_added
                        # --- END OF MODIFIED CODE FOR FILE RESTRICTIONS IN DIRECTORY ---
                    else:
                        error_count += 1
                        
                except Exception as file_error:
                    error_count += 1
                    print(f"Error processing file {raw_path}: {file_error}")
            
            # Update count and comprehensive status
            self.update_file_count()
            status_parts = []
            if added_count > 0:
                status_parts.append(f"Added {added_count} file(s)")
            if skipped_count > 0:
                status_parts.append(f"Skipped {skipped_count} duplicate(s)")
            # --- START OF ADDED CODE FOR FILE RESTRICTIONS ---
            if len(rejected_files_by_type) > 0:
                status_parts.append(f"Rejected {len(rejected_files_by_type)} unsupported type(s)")
                tkinter.messagebox.showwarning(
                    "Unsupported File Types",
                    "The following files were rejected because their types are not supported:\n\n" +
                    "\n".join(rejected_files_by_type) +
                    "\n\nOnly .wav, .csv, .tsv, .xls, and .xlsx files are allowed."
                )
            # --- END OF ADDED CODE FOR FILE RESTRICTIONS ---
                
            status_text = ". ".join(status_parts) if status_parts else "No files processed"
            status_text += f". Total: {len(self.files)}"
            self.status_label.configure(text=status_text)
            
            # Update drop zone visual feedback
            if added_count > 0:
                self.drop_label.configure(
                    text=f"✅\n\nSuccess!\n{added_count} file(s) added",
                    bg="#28a745",
                    fg="white"
                )
            # --- START OF MODIFIED CODE FOR FILE RESTRICTIONS ---
            elif len(rejected_files_by_type) > 0: # If only rejected, show error
                 self.drop_label.configure(
                    text="❌\n\nFiles rejected\nCheck message",
                    bg="#dc3545",
                    fg="white"
                )
            # --- END OF MODIFIED CODE FOR FILE RESTRICTIONS ---
            else:
                self.drop_label.configure(
                    text="ℹ️\n\nNo new files\nto add",
                    bg="#ffc107",
                    fg="black"
                )
            
            # Reset drop zone appearance after delay
            self.root.after(3000, self.reset_drop_zone)
            
        except Exception as e:
            self.status_label.configure(text=f"Error processing drop: {str(e)}")
            self.drop_frame.configure(bg="#dc3545", highlightbackground="#dc3545")
            self.drop_label.configure(
                text="❌\n\nError occurred\nTry again",
                bg="#dc3545",
                fg="white"
            )
            self.root.after(3000, self.reset_drop_zone)
            print(f"Drop error: {e}")
                
    def browse_files(self, event=None):
        """Open file dialog with file type restrictions."""
        from tkinter import filedialog
        
        # --- START OF MODIFIED CODE FOR FILE RESTRICTIONS ---
        filetypes = [
            ("WAV Audio Files", "*.wav"),
            ("CSV Files", "*.csv"),
            ("TSV Files", "*.tsv"),
            ("Excel Files", "*.xls *.xlsx"),
            ("All Supported Files", "*.wav *.csv *.tsv *.xls *.xlsx"), # Combined filter
            ("All Files", "*.*") # Option to show all files, but we'll filter after selection
        ]
        files = filedialog.askopenfilenames(
            title="Select Files",
            filetypes=filetypes # Use the new restricted filetypes
        )
        # --- END OF MODIFIED CODE FOR FILE RESTRICTIONS ---
        
        if files:
            added_count = 0
            # --- START OF ADDED CODE FOR FILE RESTRICTIONS ---
            rejected_count = 0
            rejected_file_names = []
            allowed_extensions = ('.wav', '.csv', '.tsv', '.xls', '.xlsx') # Define here too for post-selection check
            # --- END OF ADDED CODE FOR FILE RESTRICTIONS ---

            for file_path in files:
                # --- START OF ADDED CODE FOR FILE RESTRICTIONS ---
                file_ext = os.path.splitext(file_path)[1].lower()
                if file_ext in allowed_extensions:
                # --- END OF ADDED CODE FOR FILE RESTRICTIONS ---
                    if file_path not in self.files:
                        self.files.append(file_path)
                        self.add_file_to_list(file_path) # Assumes add_file_to_list exists and updates UI
                        added_count += 1
                # --- START OF ADDED CODE FOR FILE RESTRICTIONS ---
                else:
                    rejected_count += 1
                    rejected_file_names.append(os.path.basename(file_path))
                # --- END OF ADDED CODE FOR FILE RESTRICTIONS ---
            
            self.update_file_count()
            # --- START OF MODIFIED CODE FOR FILE RESTRICTIONS ---
            status_parts = []
            if added_count > 0:
                status_parts.append(f"Added {added_count} file(s) via browser.")
            if rejected_count > 0:
                status_parts.append(f"{rejected_count} file(s) rejected.")
                tkinter.messagebox.showwarning(
                    "Unsupported File Type(s)",
                    f"The following file(s) were rejected because their type is not supported:\n\n" +
                    "\n".join(rejected_file_names) +
                    "\n\nOnly .wav, .csv, .tsv, .xls, and .xlsx files are allowed."
                )

            self.status_label.configure(text=" ".join(status_parts) + f". Total: {len(self.files)}")
            # --- END OF MODIFIED CODE FOR FILE RESTRICTIONS ---
    
    def reset_drop_zone(self):
        """Reset drop zone to default appearance"""
        self.drop_frame.configure(bg="#2b2b2b", highlightbackground="gray")
        self.drop_label.configure(
            text="📁\n\nDrag & Drop Files Here\n(or click to browse)",
            bg="#2b2b2b",
            fg="gray"
        )
    
    # --- START OF MODIFIED CODE FOR FILE RESTRICTIONS IN DIRECTORY ---
    def process_directory(self, dir_path, allowed_extensions, max_files=50): # Added allowed_extensions parameter
    # --- END OF MODIFIED CODE FOR FILE RESTRICTIONS IN DIRECTORY ---
        """Process dropped directory and add files from it"""
        added_count = 0
        try:
            for root, dirs, files in os.walk(dir_path):
                for file in files:
                    if added_count >= max_files:  # Prevent too many files
                        break
                    file_path = os.path.join(root, file)
                    
                    # --- START OF ADDED CODE FOR FILE RESTRICTIONS IN DIRECTORY ---
                    file_ext = os.path.splitext(file_path)[1].lower()
                    if file_ext not in allowed_extensions:
                        continue # Skip to next file if type is not allowed
                    # --- END OF ADDED CODE FOR FILE RESTRICTIONS IN DIRECTORY ---

                    if file_path not in self.files:
                        try:
                            # Skip hidden files and very large files
                            if not file.startswith('.') and os.path.getsize(file_path) < 100 * 1024 * 1024:  # 100MB limit
                                self.files.append(file_path)
                                self.add_file_to_list(file_path) # Assumes add_file_to_list exists and updates UI
                                added_count += 1
                        except:
                            continue
                if added_count >= max_files:
                    break
        except Exception as e:
            print(f"Error processing directory {dir_path}: {e}")
        return added_count
        
    def add_file_to_list(self, file_path):
        """Add a file to the display list"""
        filename = os.path.basename(file_path)
        file_size = self.get_file_size(file_path)
        file_ext = os.path.splitext(filename)[1].lower()
        
        # Get file icon based on extension
        icon = self.get_file_icon(file_ext)
        
        file_frame = ctk.CTkFrame(self.file_list_frame, height=40)
        file_frame.pack(fill="x", pady=3, padx=5)
        file_frame.pack_propagate(False)
        
        # File info
        info_text = f"{icon} {filename}"
        if len(info_text) > 50:
            info_text = f"{icon} {filename[:45]}..."
            
        info_label = ctk.CTkLabel(
            file_frame,
            text=info_text,
            anchor="w",
            font=ctk.CTkFont(size=12)
        )
        info_label.pack(side="left", fill="x", expand=True, padx=10, pady=8)
        
        # Size label
        size_label = ctk.CTkLabel(
            file_frame,
            text=file_size,
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        size_label.pack(side="right", padx=(0, 10), pady=8)
        
        # Remove button with tooltip-like behavior
        remove_btn = ctk.CTkButton(
            file_frame,
            text="✕",
            width=25,
            height=25,
            command=lambda fp=file_path, ff=file_frame: self.remove_file(fp, ff),
            fg_color="#dc3545",
            hover_color="#c82333"
        )
        remove_btn.pack(side="right", padx=5, pady=8)
        
        # Add double-click to open file
        info_label.bind("<Double-Button-1>", lambda e, fp=file_path: self.open_file(fp))
        
        # Add right-click context menu
        info_label.bind("<Button-3>", lambda e, fp=file_path: self.show_context_menu(e, fp))
    
    def open_file(self, file_path):
        """Open file with default system application"""
        try:
            import subprocess # Original code has this import inside the try block. Will respect.
            import platform # Original code has this import inside the try block. Will respect.
            
            if platform.system() == "Windows":
                os.startfile(file_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", file_path])
            else:  # Linux
                subprocess.run(["xdg-open", file_path])
                
            self.status_label.configure(text=f"Opened: {os.path.basename(file_path)}")
        except Exception as e:
            self.status_label.configure(text=f"Failed to open file: {str(e)}")
    
    def show_context_menu(self, event, file_path):
        """Show context menu for file operations"""
        import tkinter as tk # Original code has this import inside the method. Will respect.
        
        context_menu = tk.Menu(self.root, tearoff=0)
        context_menu.add_command(
            label="Open File", 
            command=lambda: self.open_file(file_path)
        )
        context_menu.add_command(
            label="Show in Folder", 
            command=lambda: self.show_in_folder(file_path)
        )
        context_menu.add_separator()
        context_menu.add_command(
            label="Copy Path", 
            command=lambda: self.copy_to_clipboard(file_path)
        )
        context_menu.add_command(
            label="Remove from List", 
            command=lambda: self.remove_file_by_path(file_path)
        )
        
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    
    def show_in_folder(self, file_path):
        """Show file in its containing folder"""
        try:
            import subprocess # Original code has this import inside the try block. Will respect.
            import platform # Original code has this import inside the try block. Will respect.
            
            if platform.system() == "Windows":
                subprocess.run(f'explorer /select,"{file_path}"', shell=True)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", "-R", file_path])
            else:  # Linux
                folder_path = os.path.dirname(file_path)
                subprocess.run(["xdg-open", folder_path])
                
            self.status_label.configure(text=f"Showed in folder: {os.path.basename(file_path)}")
        except Exception as e:
            self.status_label.configure(text=f"Failed to show in folder: {str(e)}")
    
    def copy_to_clipboard(self, text):
        """Copy text to clipboard"""
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self.status_label.configure(text="Path copied to clipboard.")
        except Exception as e:
            self.status_label.configure(text=f"Failed to copy: {str(e)}")
    
    def remove_file_by_path(self, file_path):
        """Remove file by path (for context menu)"""
        if file_path in self.files:
            self.files.remove(file_path)
            # Refresh the entire list display
            for widget in self.file_list_frame.winfo_children():
                widget.destroy()
            for fp in self.files:
                self.add_file_to_list(fp)
            self.update_file_count()
            self.status_label.configure(text=f"Removed: {os.path.basename(file_path)}")
    
    def get_file_icon(self, extension):
        """Get appropriate icon for file type with more categories"""
        icons = {
            # Documents
            '.txt': '📄', '.doc': '📄', '.docx': '📄', '.pdf': '📕', '.rtf': '📄',
            '.odt': '📄', '.pages': '📄', '.tex': '📄',
            
            # Spreadsheets  
            '.xls': '📊', '.xlsx': '📊', '.csv': '📊', '.ods': '📊', '.numbers': '📊',
            '.tsv': '📊', # --- ADDED .tsv icon ---
            
            # Presentations
            '.ppt': '📽️', '.pptx': '📽️', '.odp': '📽️', '.key': '📽️',
            
            # Images
            '.jpg': '🖼️', '.jpeg': '🖼️', '.png': '🖼️', '.gif': '🎞️', '.bmp': '🖼️',
            '.svg': '🎨', '.tiff': '🖼️', '.webp': '🖼️', '.ico': '🖼️', '.psd': '🎨',
            
            # Audio
            '.mp3': '🎵', '.wav': '🎵', '.flac': '🎵', '.aac': '🎵', '.ogg': '🎵',
            '.m4a': '🎵', '.wma': '🎵',
            
            # Video
            '.mp4': '🎬', '.avi': '🎬', '.mkv': '🎬', '.mov': '🎬', '.wmv': '🎬',
            '.flv': '🎬', '.webm': '🎬', '.m4v': '🎬',
            
            # Archives
            '.zip': '📦', '.rar': '📦', '.7z': '📦', '.tar': '📦', '.gz': '📦',
            '.bz2': '📦', '.xz': '📦',
            
            # Code
            '.py': '🐍', '.js': '📜', '.html': '🌐', '.css': '🎨', '.java': '☕',
            '.cpp': '⚡', '.c': '⚡', '.php': '🐘', '.rb': '💎', '.go': '🐹',
            '.rs': '🦀', '.swift': '🦉', '.kt': '📱', '.scala': '📜', '.r': '📊',
            
            # Executables
            '.exe': '⚙️', '.msi': '⚙️', '.app': '📱', '.deb': '📦', '.rpm': '📦',
            '.dmg': '💿', '.iso': '💿',
            
            # Data
            '.json': '📋', '.xml': '📋', '.yaml': '📋', '.yml': '📋', '.toml': '📋',
            '.ini': '⚙️', '.cfg': '⚙️', '.conf': '⚙️',
            
            # Fonts
            '.ttf': '🔤', '.otf': '🔤', '.woff': '🔤', '.woff2': '🔤'
        }
        return icons.get(extension, '📄')
        
    def get_file_size(self, file_path):
        """Get human-readable file size"""
        try:
            size = os.path.getsize(file_path)
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024:
                    return f"{size:.1f} {unit}"
                size /= 1024
            return f"{size:.1f} TB"
        except:
            return "Unknown size"
            
    def remove_file(self, file_path, file_frame):
        """Remove a file from the list"""
        if file_path in self.files:
            self.files.remove(file_path)
        file_frame.destroy()
        self.update_file_count()
        self.status_label.configure(text=f"File removed. Total: {len(self.files)}")
        
    def clear_files(self):
        """Clear all files"""
        self.files.clear()
        for widget in self.file_list_frame.winfo_children():
            widget.destroy()
        self.update_file_count()
        self.status_label.configure(text="All files cleared.")
        
    def update_file_count(self):
        """Update the file count and total size display"""
        total_size = 0
        for file_path in self.files:
            try:
                total_size += os.path.getsize(file_path)
            except:
                continue
        
        size_str = self.format_size(total_size)
        self.count_label.configure(text=f"Files: {len(self.files)} | Size: {size_str}")
    
    def format_size(self, size_bytes):
        """Format bytes into human readable string"""
        if size_bytes == 0:
            return "0 B"
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} PB"
    
    def export_file_list(self):
        """Export the file list to a text file"""
        self.on_app_close()
        
        if export_path:
            try:
                with open(export_path, 'w', encoding='utf-8') as f:
                    f.write("File List Export\n")
                    f.write("=" * 50 + "\n")
                    f.write(f"Generated: {self.get_current_time()}\n")
                    f.write(f"Total Files: {len(self.files)}\n")
                    
                    total_size = sum(os.path.getsize(fp) for fp in self.files if os.path.exists(fp))
                    f.write(f"Total Size: {self.format_size(total_size)}\n\n")
                    
                    for i, file_path in enumerate(self.files, 1):
                        if os.path.exists(file_path):
                            size = self.format_size(os.path.getsize(file_path))
                            f.write(f"{i:3d}. {os.path.basename(file_path)}\n")
                            f.write(f"     Path: {file_path}\n")
                            f.write(f"     Size: {size}\n\n")
                
                self.status_label.configure(text=f"File list exported to {os.path.basename(export_path)}")
            except Exception as e:
                self.status_label.configure(text=f"Export failed: {str(e)}")
    
    def open_containing_folder(self):
        """Open the folder containing the first selected file"""
        if not self.files:
            self.status_label.configure(text="No files selected.")
            return
            
        try:
            import subprocess
            import platform
            
            folder_path = os.path.dirname(self.files[0])
            
            if platform.system() == "Windows":
                subprocess.run(f'explorer "{folder_path}"', shell=True)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", folder_path])
            else:  # Linux
                subprocess.run(["xdg-open", folder_path])
                
            self.status_label.configure(text=f"Opened folder: {os.path.basename(folder_path)}")
        except Exception as e:
            self.status_label.configure(text=f"Failed to open folder: {str(e)}")
    
    def get_current_time(self):
        """Get current time as formatted string"""
        # from datetime import datetime # No longer need this here if globally imported
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
    def run(self):
        """Start the application"""
        self.root.mainloop()

# if __name__ == "__main__":
#     app = DragDropApp()
#     app.run()