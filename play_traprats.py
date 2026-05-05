#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  4 15:03:10 2026

@author: jessie
"""

import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import threading
import os
import io
import sys

# Import your existing classes
from board import *
from imgreader import *
from tiles import *


class PuzzleSolverGUI:
    """
    GUI application for solving enclose.horse puzzles.

    Allows users to upload a puzzle image, configure board parameters,
    solve the puzzle, and display the solution.
    """

    def __init__(self, root):
        """
        Initialize the GUI.

        Parameters
        ----------
        root : tk.Tk
            The root tkinter window.
        """
        self.root = root
        self.root.title("enclose.horse solver")
        self.root.geometry("1100x750")
        self.root.configure(bg="#2b2b2b")

        # State variables
        self.image_path = None
        self.board = None
        self.visualizer = BoardVisualizer()
        self.is_solving = False
        self.is_solved = False  # Track if puzzle has been solved
        self.original_filename = None  # Store original filename for saving

        # Configure grid weights for resizing
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        self._create_widgets()

    def _create_widgets(self):
        """Create all GUI widgets."""

        # left panel controls
        left_panel = tk.Frame(self.root, bg="#363636", width=280)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        left_panel.grid_propagate(False)

        # title
        title_label = tk.Label(
            left_panel,
            text="🐀 solver",
            font=("Helvetica", 18, "bold"),
            bg="#363636",
            fg="white"
        )
        title_label.pack(pady=20)

        # Upload Button
        self.upload_btn = tk.Button(
            left_panel,
            text="📁 Upload Image",
            font=("Helvetica", 12),
            command=self._upload_image,
            bg="#4a9eff",
            fg="black",
            width=20,
            height=2,
            cursor="hand2"
        )
        self.upload_btn.pack(pady=10)

        # File name display
        self.file_label = tk.Label(
            left_panel,
            text="No file selected",
            font=("Helvetica", 9),
            bg="#363636",
            fg="#888888",
            wraplength=250
        )
        self.file_label.pack(pady=(0, 10))

        #  board config frame
        config_frame = tk.LabelFrame(
            left_panel,
            text="Board Configuration",
            font=("Helvetica", 10, "bold"),
            bg="#363636",
            fg="white",
            padx=10,
            pady=10
        )
        config_frame.pack(pady=10, padx=10, fill=tk.X)

        # Rows input
        row_frame = tk.Frame(config_frame, bg="#363636")
        row_frame.pack(fill=tk.X, pady=5)

        tk.Label(
            row_frame, text="Rows:",
            bg="#363636", fg="white", font=("Helvetica", 10),
            width=10, anchor="w"
        ).pack(side=tk.LEFT)

        self.rows_var = tk.StringVar(value="10")
        self.rows_entry = tk.Entry(
            row_frame, textvariable=self.rows_var,
            width=10, font=("Helvetica", 10)
        )
        self.rows_entry.pack(side=tk.LEFT, padx=5)

        # Cols input
        col_frame = tk.Frame(config_frame, bg="#363636")
        col_frame.pack(fill=tk.X, pady=5)

        tk.Label(
            col_frame, text="Columns:",
            bg="#363636", fg="white", font=("Helvetica", 10),
            width=10, anchor="w"
        ).pack(side=tk.LEFT)

        self.cols_var = tk.StringVar(value="10")
        self.cols_entry = tk.Entry(
            col_frame, textvariable=self.cols_var,
            width=10, font=("Helvetica", 10)
        )
        self.cols_entry.pack(side=tk.LEFT, padx=5)

        # Walls input
        walls_frame = tk.Frame(config_frame, bg="#363636")
        walls_frame.pack(fill=tk.X, pady=5)

        tk.Label(
            walls_frame, text="Walls:",
            bg="#363636", fg="white", font=("Helvetica", 10),
            width=10, anchor="w"
        ).pack(side=tk.LEFT)

        self.walls_var = tk.StringVar(value="10")
        self.walls_entry = tk.Entry(
            walls_frame, textvariable=self.walls_var,
            width=10, font=("Helvetica", 10)
        )
        self.walls_entry.pack(side=tk.LEFT, padx=5)

        # Load Board Button
        self.load_btn = tk.Button(
            left_panel,
            text="🔍 Load Board",
            font=("Helvetica", 12),
            command=self._load_board,
            bg="#28a745",
            fg="black",
            width=20,
            height=2,
            state=tk.DISABLED,
            cursor="hand2"
        )
        self.load_btn.pack(pady=10)

        # Save Solution Button
        self.save_btn = tk.Button(
            left_panel,
            text="💾 Save Image",
            font=("Helvetica", 12),
            command=self._save_solution,
            bg="#17a2b8",
            fg="black",
            width=20,
            height=2,
            state=tk.DISABLED,
            cursor="hand2"
        )
        self.save_btn.pack(pady=10)

        # Solve Button
        self.solve_btn = tk.Button(
            left_panel,
            text="🧩 Solve Puzzle",
            font=("Helvetica", 12),
            command=self._solve_puzzle,
            bg="#ffc107",
            fg="black",
            width=20,
            height=2,
            state=tk.DISABLED,
            cursor="hand2"
        )
        self.solve_btn.pack(pady=10)

        # score display
        score_frame = tk.Frame(left_panel, bg="#2d5a2d",
                               relief=tk.RAISED, bd=2)
        score_frame.pack(pady=20, padx=10, fill=tk.X)

        tk.Label(
            score_frame, text="SCORE",
            font=("Helvetica", 12, "bold"),
            bg="#2d5a2d", fg="white"
        ).pack(pady=(10, 0))

        self.score_label = tk.Label(
            score_frame,
            text="---",
            font=("Helvetica", 36, "bold"),
            bg="#2d5a2d",
            fg="#00ff00"
        )
        self.score_label.pack(pady=(0, 10))

        # stats
        stats_label = tk.Label(
            left_panel,
            text="Stats:",
            font=("Helvetica", 10, "bold"),
            bg="#363636",
            fg="white",
            anchor="w"
        )
        stats_label.pack(pady=(10, 0), padx=10, anchor="w")

        self.stats_text = tk.Text(
            left_panel,
            height=10,
            width=30,
            font=("Courier", 9),
            bg="#2b2b2b",
            fg="#aaaaaa",
            relief=tk.FLAT,
            state=tk.DISABLED
        )
        self.stats_text.pack(pady=5, padx=10, fill=tk.X)

        # Status bar
        self.status_label = tk.Label(
            left_panel,
            text="Ready. Upload an image to begin.",
            font=("Helvetica", 9),
            bg="#363636",
            fg="#888888",
            wraplength=260
        )
        self.status_label.pack(side=tk.BOTTOM, pady=10)

        # right panel (board)
        right_panel = tk.Frame(self.root, bg="#1e1e1e")
        right_panel.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        # Canvas for board display
        self.canvas = tk.Canvas(
            right_panel,
            bg="#1e1e1e",
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Store image reference to prevent garbage collection
        self.photo_image = None

    def _upload_image(self):
        """Open file dialog to upload a puzzle image."""
        filetypes = [
            ("PNG files", "*.png"),
            ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
            ("All files", "*.*")
        ]

        path = filedialog.askopenfilename(
            title="Select Puzzle Image",
            filetypes=filetypes
        )

        if path:
            self.image_path = path
            self.original_filename = os.path.splitext(
                os.path.basename(path))[0]
            self._display_uploaded_image(path)
            self.load_btn.config(state=tk.NORMAL)
            self.file_label.config(text=os.path.basename(path))
            self.status_label.config(
                text="Image loaded. Configure board and click 'Load Board'.")

            # Reset state
            self.board = None
            self.solve_btn.config(state=tk.DISABLED)
            self.save_btn.config(state=tk.DISABLED)
            self.score_label.config(text="---")
            self._clear_stats()

    def _display_uploaded_image(self, path):
        """Display the raw uploaded image."""
        try:
            image = Image.open(path)
            self._display_pil_image(image)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {e}")

    def _display_pil_image(self, image):
        """
        Display a PIL Image on the canvas, scaled to fit.

        Parameters
        ----------
        image : PIL.Image
            The image to display.
        """
        self.canvas.update()
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        if canvas_width <= 1 or canvas_height <= 1:
            canvas_width = 750
            canvas_height = 700

        # Scale to fit canvas
        img_width, img_height = image.size
        scale = min(canvas_width / img_width, canvas_height / img_height, 1.0)

        new_width = int(img_width * scale)
        new_height = int(img_height * scale)

        if new_width > 0 and new_height > 0:
            image = image.resize((new_width, new_height), Image.NEAREST)

        self.photo_image = ImageTk.PhotoImage(image)

        x = canvas_width // 2
        y = canvas_height // 2

        self.canvas.delete("all")
        self.canvas.create_image(
            x, y, image=self.photo_image, anchor=tk.CENTER)

    def _display_board(self, board):
        """
        Render and display a Board object.

        Parameters
        ----------
        board : Board
            The board to display.
        """
        rendered = self.visualizer.render(board)
        image = Image.fromarray(rendered)
        self._display_pil_image(image)

    def _load_board(self):
        """Load and parse the board from the uploaded image."""
        try:
            rows = int(self.rows_var.get())
            cols = int(self.cols_var.get())
            walls = int(self.walls_var.get())

            if rows <= 0 or cols <= 0 or walls < 0:
                raise ValueError("Values must be positive")

        except ValueError as e:
            messagebox.showerror(
                "Invalid Input", f"Please enter valid numbers.\n{e}")
            return

        self.status_label.config(text="Parsing board...")
        self.root.update()

        try:
            self.board = Board(rows, cols, walls, image_path=self.image_path)
            self._display_board(self.board)

            self.solve_btn.config(state=tk.NORMAL)
            self.is_solved = False
            self.save_btn.config(state=tk.DISABLED)
            self.status_label.config(
                text="Board loaded! Click 'Solve Puzzle' to find solution.")
            self.score_label.config(text="---")
            self._clear_stats()

        except Exception as e:
            messagebox.showerror("Parse Error", f"Failed to parse board:\n{e}")
            self.status_label.config(text="Failed to parse board.")

    def _solve_puzzle(self):
        """Solve the puzzle in a background thread."""
        if self.board is None:
            return

        self.status_label.config(text="Solving puzzle... Please wait.")
        self.solve_btn.config(state=tk.DISABLED)
        self.load_btn.config(state=tk.DISABLED)
        self.upload_btn.config(state=tk.DISABLED)
        self.save_btn.config(state=tk.DISABLED)
        self.is_solving = True

        thread = threading.Thread(target=self._run_solver)
        thread.daemon = True
        thread.start()

    def _run_solver(self):
        """Run the solver (called in background thread)."""
        try:
            self.board.solve_puzzle()
            self.root.after(0, self._on_solve_complete)
        except Exception as e:
            self.root.after(0, lambda: self._on_solve_error(str(e)))

    def _on_solve_complete(self):
        """Called when solver completes successfully."""
        self.is_solving = False
        self.is_solved = True

        # Display solved board
        self._display_board(self.board)

        # Get and display score
        try:
            score = self.board.score
            self.score_label.config(text=str(score))
        except Exception:
            self.score_label.config(text="N/A")

        # Display stats
        self._update_stats()

        # Re-enable buttons
        self.solve_btn.config(state=tk.NORMAL)
        self.load_btn.config(state=tk.NORMAL)
        self.upload_btn.config(state=tk.NORMAL)
        self.status_label.config(
            text="Solved! Click 'Save Solution' to save the image.")
        self.save_btn.config(state=tk.NORMAL)

    def _on_solve_error(self, error_message):
        """Called when solver encounters an error."""
        self.is_solving = False
        messagebox.showerror(
            "Solver Error", f"An error occurred:\n{error_message}")
        self.status_label.config(text="Failed to solve puzzle.")

        self.solve_btn.config(state=tk.NORMAL)
        self.load_btn.config(state=tk.NORMAL)
        self.upload_btn.config(state=tk.NORMAL)

    def _save_solution(self):
        """Save the solution image as a PNG file."""
        if not self.is_solved or self.board is None:
            messagebox.showwarning(
                "No Solution", "Please solve the puzzle first.")
            return

        # Generate default filename
        default_filename = f"sol_{self.original_filename}.png"

        # Open save dialog
        filetypes = [
            ("PNG files", "*.png"),
            ("All files", "*.*")
        ]

        save_path = filedialog.asksaveasfilename(
            title="Save Solution Image",
            defaultextension=".png",
            initialfile=default_filename,
            filetypes=filetypes
        )

        if save_path:
            try:
                self.visualizer.save(self.board, save_path)
                self.status_label.config(
                    text=f"Solution saved to {os.path.basename(save_path)}")
                messagebox.showinfo(
                    "Saved", f"Solution saved successfully!\n\n{save_path}")
            except Exception as e:
                messagebox.showerror(
                    "Save Error", f"Failed to save image:\n{e}")
                self.status_label.config(text="Failed to save solution.")

    def _update_stats(self):
        """Update the stats display by capturing board.stats() output."""
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete(1.0, tk.END)

        try:
            # Capture stdout from board.stats()
            old_stdout = sys.stdout
            sys.stdout = buffer = io.StringIO()

            self.board.stats()

            stats_output = buffer.getvalue()
            sys.stdout = old_stdout

            self.stats_text.insert(tk.END, stats_output)
        except Exception as e:
            self.stats_text.insert(tk.END, f"Stats unavailable: {e}")

        self.stats_text.config(state=tk.DISABLED)

    def _clear_stats(self):
        """Clear the stats display."""
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.config(state=tk.DISABLED)


def main():
    """Main entry point for the GUI application."""
    root = tk.Tk()

    # High DPI awareness for Windows
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

    app = PuzzleSolverGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
