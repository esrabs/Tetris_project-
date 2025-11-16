from interface import Interface, KST
import random
from dataclasses import dataclass
import numpy as np

# --- dimensions ---
GRID_WIDTH  = 10
GRID_HEIGHT = 20
PANEL_WIDTH = 16  # largeur du panneau de droite

# --- palette (noms attendus par Interface.COULEUR) ---
PALETTE = ["cyan", "bleu", "orange", "jaune", "vert", "violet", "rouge", "gris"]
NAME_TO_IDX = {name: i + 1 for i, name in enumerate(PALETTE)}   # 1..N en grille
IDX_TO_NAME = {i + 1: name for i, name in enumerate(PALETTE)}


@dataclass(frozen=True)
class Point:
    x: int
    y: int


class Tetramino:
    SHAPES = [
        [[1, 1, 1, 1]],                 # I
        [[1, 0, 0], [1, 1, 1]],         # J
        [[0, 0, 1], [1, 1, 1]],         # L
        [[1, 1], [1, 1]],               # O
        [[0, 1, 1], [1, 1, 0]],         # S
        [[0, 1, 0], [1, 1, 1]],         # T
        [[1, 1, 0], [0, 1, 1]],         # Z
    ]
    COLORS = ["cyan", "bleu", "orange", "jaune", "vert", "violet", "rouge"]

    def __init__(self, shape_idx=None):
        if shape_idx is None:
            shape_idx = random.randrange(len(self.SHAPES))
        self.shape_idx = shape_idx
        self.shape = np.array(self.SHAPES[shape_idx], dtype=int)
        self.color_name = self.COLORS[shape_idx] if self.COLORS[shape_idx] in NAME_TO_IDX else "blanc"
        self.rotation = 0
        self.position = Point(GRID_WIDTH // 2 - self.shape.shape[1] // 2, 0)

    def rotate(self):
        self.rotation = (self.rotation + 1) % 4

    def image(self):
        """Points (x,y) occupés par la pièce, rotation et position incluses."""
        rot = np.rot90(self.shape, -self.rotation)
        pts = []
        for y, row in enumerate(rot):
            for x, cell in enumerate(row):
                if cell:
                    pts.append(Point(x + self.position.x, y + self.position.y))
        return pts


class Board:
    def __init__(self, interface: Interface):
        self.interface = interface
        self.grid = np.zeros((GRID_HEIGHT, GRID_WIDTH), dtype=int)  # 0=vide, >0=index couleur
        self.tetraminos = [Tetramino()]
        self.active = 0
        self.next_tetramino = Tetramino()
        self.score = 0
        self.game_over = False

    # ---------- collisions ----------
    def overlap_board(self, pts):
        for p in pts:
            if p.x < 0 or p.x >= GRID_WIDTH or p.y < 0 or p.y >= GRID_HEIGHT:
                return True
            if self.grid[p.y, p.x] != 0:
                return True
        return False

    def overlap_other(self, idx, pts):
        if len(self.tetraminos) < 2:
            return False
        other_pts = {(p.x, p.y) for p in self.tetraminos[1 - idx].image()}
        return any((p.x, p.y) in other_pts for p in pts)

    # ---------- actions ----------
    def try_rotate(self, idx):
        t = self.tetraminos[idx]
        old_rot, old_pos = t.rotation, t.position
        t.rotate()
        pts = t.image()
        if not self.overlap_board(pts) and not self.overlap_other(idx, pts):
            return True
        # wall-kick horizontal
        for dx in (-1, 1, -2, 2):
            t.position = Point(old_pos.x + dx, old_pos.y)
            pts = t.image()
            if not self.overlap_board(pts) and not self.overlap_other(idx, pts):
                return True
        # échec
        t.rotation = old_rot
        t.position = old_pos
        return False

    def try_move(self, idx, dx):
        t = self.tetraminos[idx]
        new_pos = Point(t.position.x + dx, t.position.y)
        # tentative de poussée si 2 pièces
        if len(self.tetraminos) == 2:
            # simuler le déplacement
            sim_rot = t.rotation
            sim_shape = t.shape  # pas de modif
            # construire points simulés
            rot = np.rot90(sim_shape, -sim_rot)
            sim_pts = [Point(x + new_pos.x, y + new_pos.y)
                       for y, row in enumerate(rot) for x, c in enumerate(row) if c]
            if self.overlap_other(idx, sim_pts):
                other = self.tetraminos[1 - idx]
                other_new = Point(other.position.x + dx, other.position.y)
                rot_o = np.rot90(other.shape, -other.rotation)
                other_pts = [Point(x + other_new.x, y + other_new.y)
                             for y, row in enumerate(rot_o) for x, c in enumerate(row) if c]
                if self.overlap_board(other_pts):
                    return False  # poussée impossible
                # pousser l'autre
                other.position = other_new

        # déplacer la pièce active
        t.position = new_pos
        if self.overlap_board(t.image()):
            t.position = Point(t.position.x - dx, t.position.y)
            return False
        return True

    def soft_drop(self, idx):
        if idx >= len(self.tetraminos):
            return False
        t = self.tetraminos[idx]
        t.position = Point(t.position.x, t.position.y + 1)
        if self.overlap_board(t.image()) or self.overlap_other(idx, t.image()):
            # verrouiller
            t.position = Point(t.position.x, t.position.y - 1)
            self.lock_piece(idx)
            return False
        return True

    def lock_piece(self, idx):
        t = self.tetraminos[idx]
        col_idx = NAME_TO_IDX.get(t.color_name, NAME_TO_IDX.get("gris", 1))
        for p in t.image():
            if 0 <= p.y < GRID_HEIGHT and 0 <= p.x < GRID_WIDTH:
                self.grid[p.y, p.x] = col_idx
        # retirer la pièce tombante
        self.tetraminos.pop(idx)
        if self.tetraminos:
            self.active = 0

        lines = self.clear_lines()
        self.score += [0, 40, 200, 300, 1200][lines]

        # apparition des nouvelles pièces
        if not self.tetraminos:
            if lines >= 2:
                n1 = self.next_tetramino
                n2 = Tetramino()
                n1.position = Point(GRID_WIDTH // 2 - n1.shape.shape[1] // 2, 0)
                n2.position = Point(min(GRID_WIDTH - 2, GRID_WIDTH // 2 + GRID_WIDTH // 3), 0)
                self.tetraminos = [n1, n2]
                self.active = 0
            else:
                self.tetraminos = [self.next_tetramino]
                self.active = 0
            self.next_tetramino = Tetramino()

            # game over si spawn collisionne
            if self.overlap_board(self.tetraminos[0].image()) or (
                len(self.tetraminos) == 2 and self.overlap_board(self.tetraminos[1].image())
            ):
                self.game_over = True

    def clear_lines(self):
        full = [y for y in range(GRID_HEIGHT) if all(self.grid[y, x] != 0 for x in range(GRID_WIDTH))]
        if not full:
            return 0
        remaining = np.delete(self.grid, full, axis=0)
        new_rows = np.zeros((len(full), GRID_WIDTH), dtype=int)
        self.grid = np.vstack((new_rows, remaining))
        return len(full)

    # ---------- rendu ----------
    def draw_playfield(self):
        # fond du plateau
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                self.interface.curseur(1 + x, y)
                self.interface.write(" ", bgcolor=self.interface.COULEUR["noir"])
        # blocs posés
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                val = self.grid[y, x]
                if val:
                    name = IDX_TO_NAME.get(val, "blanc")
                    self.interface.curseur(1 + x, y)
                    self.interface.write(" ", bgcolor=self.interface.COULEUR.get(name, self.interface.COULEUR["blanc"]))
        # pièces en chute
        for t in self.tetraminos:
            color = self.interface.COULEUR.get(t.color_name, self.interface.COULEUR["blanc"])
            for p in t.image():
                if 0 <= p.x < GRID_WIDTH and 0 <= p.y < GRID_HEIGHT:
                    self.interface.curseur(1 + p.x, p.y)
                    self.interface.write(" ", bgcolor=color)

    def draw_border(self):
        # Couleur des bords (texte fin)
        fg = self.interface.COULEUR["gris"]

        # Bordures latérales fines
        for y in range(GRID_HEIGHT):
            self.interface.curseur(0, y)
            self.interface.write("│", fgcolor=fg)              # gauche
            self.interface.curseur(GRID_WIDTH + 1, y)
            self.interface.write("│", fgcolor=fg)              # droite du plateau

        # Ligne du bas fine
        for x in range(GRID_WIDTH + 2):
            self.interface.curseur(x, GRID_HEIGHT)
            self.interface.write("─", fgcolor=fg)

        # Ligne de séparation panneau (1 trait fin)
        for y in range(GRID_HEIGHT):
            self.interface.curseur(GRID_WIDTH + 2, y)
            self.interface.write("│", fgcolor=fg)

    def draw_panel(self):
        base_x = GRID_WIDTH + 4
        # Titre
        self.interface.curseur(base_x, 1)
        self.interface.write("Prochaine :")
        # zone d'aperçu 6x4
        for yy in range(3, 7):
            for xx in range(base_x, base_x + 6):
                self.interface.curseur(xx, yy)
                self.interface.write(" ", bgcolor=self.interface.COULEUR["noir"])
        # dessiner la prochaine pièce (non rotée)
        t = self.next_tetramino
        for y, row in enumerate(t.shape):
            for x, c in enumerate(row):
                if c:
                    self.interface.curseur(base_x + 1 + x, 3 + y)
                    self.interface.write(" ", bgcolor=self.interface.COULEUR.get(t.color_name, self.interface.COULEUR["blanc"]))
        # score
        self.interface.curseur(base_x, 9)
        self.interface.write(f"Score : {self.score}")
        # barème
        y0 = 11
        for i, s in enumerate(["1L : +40", "2L : +200", "3L : +300", "4L : +1200"]):
            self.interface.curseur(base_x, y0 + i)
            self.interface.write(s)

    def render(self):
        self.draw_playfield()
        self.draw_border()
        self.draw_panel()
        self.interface.mise_a_jour()


def main():
    # largeur totale = plateau (10) + 2 bordures + 1 séparation + panneau
    interface = Interface(GRID_WIDTH + 2 + PANEL_WIDTH, GRID_HEIGHT + 1, "Tetris (grille)")
    board = Board(interface)

    tempo = 15       # vitesse boucle
    drop_every = 10  # gravité : descend toutes les N frames
    frame = 0

    while not board.game_over:
        key = interface.lire_touche()
        if key == KST.GAUCHE:
            board.try_move(board.active, -1)
        elif key == KST.DROITE:
            board.try_move(board.active, 1)
        elif key == KST.BAS:
            board.soft_drop(board.active)
        elif key == KST.HAUT:
            board.try_rotate(board.active)
        elif key == KST.ESPACE and len(board.tetraminos) == 2:
            board.active = 1 - board.active  # alterner la pièce active

        # gravité
        frame = (frame + 1) % 1_000_000
        if frame % drop_every == 0:
            if len(board.tetraminos) == 2:
                first, second = board.active, 1 - board.active
                board.soft_drop(first)
                if len(board.tetraminos) == 2:
                    board.soft_drop(second)
            else:
                board.soft_drop(board.active)

        board.render()
        interface.pause(tempo)

    # écran fin
    interface.curseur(2, GRID_HEIGHT // 2)
    interface.write("Game Over", fgcolor=interface.COULEUR["rouge"])
    interface.mise_a_jour()
    interface.pause(3)


if __name__ == "__main__":
    main()
