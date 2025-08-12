#pip install python-chess
#pip install python-chess Pillow

import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import chess.pgn
import io
import os

BOARD_SIZE = 8
SQUARE_SIZE = 60

class PGNViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PGN Visual Chess Viewer")

        # PGN input
        tk.Label(root, text="Paste PGN below:").pack()
        self.pgn_text = tk.Text(root, height=6)
        self.pgn_text.pack(fill=tk.BOTH, padx=10, pady=5)

        # Load button
        tk.Button(root, text="Load PGN", command=self.load_pgn).pack(pady=5)

        # Canvas for board
        self.canvas = tk.Canvas(root, width=BOARD_SIZE*SQUARE_SIZE, height=BOARD_SIZE*SQUARE_SIZE)
        self.canvas.pack(pady=10)

        # Navigation buttons
        nav_frame = tk.Frame(root)
        nav_frame.pack()

        self.prev_btn = tk.Button(nav_frame, text="<< Prev", command=self.prev_move, state=tk.DISABLED)
        self.prev_btn.pack(side=tk.LEFT, padx=10)

        self.next_btn = tk.Button(nav_frame, text="Next >>", command=self.next_move, state=tk.DISABLED)
        self.next_btn.pack(side=tk.LEFT, padx=10)

        tk.Button(nav_frame, text="Exit", command=root.quit).pack(side=tk.LEFT, padx=10)

        self.images = {}
        self.move_list = []
        self.board = None
        self.move_index = 0

        self.load_images()

    def load_images(self):
        pieces = ['P','R','N','B','Q','K']
        for color in ['w', 'b']:
            for piece in pieces:
                img = Image.open(f"pieces/{color}{piece}.png").resize((SQUARE_SIZE, SQUARE_SIZE))
                self.images[color + piece] = ImageTk.PhotoImage(img)

    def load_pgn(self):
        pgn_str = self.pgn_text.get("1.0", tk.END).strip()
        if not pgn_str:
            messagebox.showwarning("Empty Input", "Please paste a PGN string.")
            return

        try:
            game = chess.pgn.read_game(io.StringIO(pgn_str))
            self.board = game.board()
            self.move_list = list(game.mainline_moves())
            self.move_index = 0
            self.prev_btn.config(state=tk.DISABLED)
            self.next_btn.config(state=tk.NORMAL)
            self.draw_board()
        except Exception as e:
            messagebox.showerror("PGN Error", f"Failed to parse PGN: {e}")

    def draw_board(self):
        self.canvas.delete("all")
        colors = ["#EEEED2", "#769656"]

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                color = colors[(row + col) % 2]
                x1 = col * SQUARE_SIZE
                y1 = row * SQUARE_SIZE
                x2 = x1 + SQUARE_SIZE
                y2 = y1 + SQUARE_SIZE
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color)

        if not self.board:
            return

        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                row = 7 - chess.square_rank(square)
                col = chess.square_file(square)
                x = col * SQUARE_SIZE
                y = row * SQUARE_SIZE
                key = ('w' if piece.color else 'b') + piece.symbol().upper()
                img = self.images.get(key)
                if img:
                    self.canvas.create_image(x, y, anchor=tk.NW, image=img)

    def next_move(self):
        if self.move_index < len(self.move_list):
            self.board.push(self.move_list[self.move_index])
            self.move_index += 1
            self.draw_board()

        if self.move_index >= len(self.move_list):
            self.next_btn.config(state=tk.DISABLED)
        self.prev_btn.config(state=tk.NORMAL)

    def prev_move(self):
        if self.move_index > 0:
            self.board.pop()
            self.move_index -= 1
            self.draw_board()

        if self.move_index <= 0:
            self.prev_btn.config(state=tk.DISABLED)
        self.next_btn.config(state=tk.NORMAL)

# Launch app
if __name__ == "__main__":
    if not os.path.exists("pieces"):
        print("You need a 'pieces' folder with 12 PNG images like wP.png, bK.png, etc.")
    else:
        root = tk.Tk()
        app = PGNViewerApp(root)
        root.mainloop()
