from PyQt5.QtWidgets import (
    QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout,
    QGridLayout, QComboBox, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer, QRect, QElapsedTimer
from PyQt5.QtGui import QFont, QColor, QPainter, QPen
from ranking.name_prompt import prompt_player_name
import random


class Cell(QPushButton):
    COLORS = {
        1: "#00FFFF", 2: "#00CCFF", 3: "#0099FF", 4: "#0066FF",
        5: "#0044FF", 6: "#00AAFF", 7: "#66DDFF", 8: "#FFFFFF"
    }

    def __init__(self, x, y, parent):
        super().__init__()
        self.x, self.y = x, y
        self.parent = parent
        self.is_mine = False
        self.is_revealed = False
        self.is_flagged = False
        self.setFixedSize(34, 34)
        self.setFont(QFont("Courier New", 12, QFont.Bold))
        self.setStyleSheet(self.hidden_style())
        


    def hidden_style(self):
        return """
            QPushButton {
                background-color: #000;
                border: 1px solid #00FFFF;
                color: #00FFFF;
            }
            QPushButton:hover {
                background-color: #002233;
            }
        """

    def revealed_style(self, color="#00FF00"):
        return f"""
            QPushButton {{
                background-color: #111;
                border: 1px solid #004466;
                color: {color};
            }}
        """

    def mousePressEvent(self, event):
        if self.parent.game_over:
            return
        if event.button() == Qt.RightButton:
            self.toggle_flag()
        elif event.button() == Qt.LeftButton:
            self.reveal()

    def toggle_flag(self):
        if self.is_revealed:
            return
        self.is_flagged = not self.is_flagged
        self.setText("🚩" if self.is_flagged else "")
        self.parent.update_counters()

    def reveal(self):
        if self.is_flagged or self.is_revealed or self.parent.game_over:
            return

        # Primer clic: colocar minas evitando el área inicial
        if self.parent.first_click:
            self.parent.place_mines_safe(self.x, self.y)
            self.parent.first_click = False
        self.is_revealed = True

        if self.is_mine:
            self.setText("💣")
            self.setStyleSheet("background-color: #FF0000; color: white; border: 1px solid #550000;")
            self.parent.trigger_game_over(False)
        else:
            count = self.parent.count_adjacent_mines(self.x, self.y)
            if count > 0:
                color = self.COLORS.get(count, "#FFFFFF")
                self.setText(str(count))
                self.setStyleSheet(self.revealed_style(color))
            else:
                self.setText("")
                self.setStyleSheet(self.revealed_style())
                self.parent.reveal_neighbors(self.x, self.y)

            self.parent.check_win()
            self.parent.update_counters()


class RetroMinesweeper(QWidget):
    def __init__(self, stacked_widget=None):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.rows = self.cols = 10
        self.mines = 10
        self.flags = 0
        self.cells = {}
        self.game_over = False
        self.first_click = True
        self.timer = QElapsedTimer()
        self.time_elapsed = 0

        self.setStyleSheet("background-color: black;")
        self.init_ui()
        QTimer.singleShot(100, self.start_game)  # asegura render antes del tablero
        self.message_label = QLabel("", self)
        self.message_label.setAlignment(Qt.AlignCenter)
        self.message_label.setStyleSheet("""
    color: #00FFFF;
    background-color: rgba(0, 20, 20, 180);
    border: 2px solid #00FFFF;
    border-radius: 8px;
    font-size: 28px;
    font-family: 'Courier New';
""")
        self.message_label.hide()



    def init_ui(self):
        # Título
        self.title = QLabel("💣 MINESWEEPER ")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setFont(QFont("Courier New", 28, QFont.Bold))
        self.title.setStyleSheet("color: #00FFFF; margin: 10px;")

        # Info
        self.info_label = QLabel("🚩 0/0")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setFont(QFont("Courier New", 14))
        self.info_label.setStyleSheet("color: #00FFFF; margin: 8px;")

        # Dificultad
        self.difficulty_box = QComboBox()
        self.difficulty_box.addItems(["FÁCIL", "NORMAL", "DIFÍCIL"])
        self.difficulty_box.setStyleSheet("""
    QComboBox {
        color: #00FFFF;
        background-color: #111;
        border: 1px solid #00FFFF;
        font-family: 'Courier New';
        font-size: 14px;
        padding: 4px;
    }
""")
        self.difficulty_box.currentIndexChanged.connect(self.change_difficulty)

        # Botones
        self.btn_restart = QPushButton("🔁 REINICIAR")
        self.btn_back = QPushButton("⬅ MENÚ")
        for b in [self.btn_restart, self.btn_back]:
            b.setFixedSize(150, 40)
            b.setFont(QFont("Courier New", 12, QFont.Bold))
            b.setStyleSheet(self.button_style())

        self.btn_restart.clicked.connect(self.start_game)
        self.btn_back.clicked.connect(self.back_to_menu)

        # HUD superior
        hud = QHBoxLayout()
        hud.setAlignment(Qt.AlignCenter)
        hud.addWidget(self.btn_restart)
        hud.addWidget(self.btn_back)
        hud.addWidget(QLabel("DIFICULTAD:", self))
        hud.addWidget(self.difficulty_box)

        # Área del tablero
        self.grid = QGridLayout()
        self.grid.setSpacing(1)
        self.grid.setAlignment(Qt.AlignCenter)

        # Marco central
        self.play_area = QWidget()
        self.play_area.setLayout(self.grid)
        self.play_area.setStyleSheet("background-color: black; border: 4px solid #00FFFF;")

        # Overlay de mensaje (para Win/Lose)
        self.message_label = QLabel("", self)
        self.message_label.setAlignment(Qt.AlignCenter)
        self.message_label.setFont(QFont("Courier New", 28, QFont.Bold))
        self.message_label.setStyleSheet("color: #00FFFF;")
        self.message_label.hide()

        # Layout principal
        main = QVBoxLayout(self)
        main.setAlignment(Qt.AlignCenter)
        main.addWidget(self.title)
        main.addLayout(hud)
        main.addWidget(self.info_label)
        main.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))
        main.addWidget(self.play_area, alignment=Qt.AlignCenter)
        main.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.setLayout(main)

    def button_style(self):
        return """
        QPushButton {
            background-color: #111;
            color: #00FFFF;
            border: 2px solid #00FFFF;
            border-radius: 6px;
        }
        QPushButton:hover {
            background-color: #00FFFF;
            color: black;
        }
    """

    def start_game(self):
        self.timer.start()

        for i in reversed(range(self.grid.count())):
            widget = self.grid.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        self.cells.clear()
        self.flags = 0
        self.game_over = False
        self.first_click = True
        self.message_label.hide()

        for x in range(self.rows):
            for y in range(self.cols):
                c = Cell(x, y, self)
                self.grid.addWidget(c, x, y, Qt.AlignCenter)
                self.cells[(x, y)] = c

        self.update_counters()


    def change_difficulty(self):
        level = self.difficulty_box.currentText()
        if level == "FÁCIL":
            self.rows, self.cols, self.mines = 8, 8, 10
        elif level == "NORMAL":
            self.rows, self.cols, self.mines = 12, 12, 25
        else:
            self.rows, self.cols, self.mines = 16, 16, 45
        self.start_game()

    def place_mines(self):
        positions = random.sample(list(self.cells.keys()), self.mines)
        for pos in positions:
            self.cells[pos].is_mine = True

    def place_mines_safe(self, first_x, first_y):
        protected = {(first_x + dx, first_y + dy) for dx in [-1, 0, 1] for dy in [-1, 0, 1]}
        positions = []
        for pos in self.cells.keys():
            if pos not in protected:
                positions.append(pos)
        mines = random.sample(positions, self.mines)
        for pos in mines:
            self.cells[pos].is_mine = True


    def count_adjacent_mines(self, x, y):
        count = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if (nx, ny) in self.cells and self.cells[(nx, ny)].is_mine:
                    count += 1
        return count

    def reveal_neighbors(self, x, y):
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nx, ny = x + dx, y + dy
                if (nx, ny) in self.cells:
                    n = self.cells[(nx, ny)]
                    if not n.is_revealed and not n.is_mine:
                        n.reveal()

    def update_counters(self):
        flags = sum(1 for c in self.cells.values() if c.is_flagged)
        remaining = sum(1 for c in self.cells.values() if not c.is_revealed)
        self.info_label.setText(f"🚩 {flags}/{self.mines}   ⏳ Celdas: {remaining}")

    def trigger_game_over(self, won):
        self.game_over = True
        for c in self.cells.values():
            if c.is_mine:
                c.setText("💣")
                c.setStyleSheet("background-color: #500000; color: #FFAAAA; border: 1px solid #FF0000;")

        self.show_message("🎯 ¡GANASTE!" if won else "💀 GAME OVER 💀")
        if won:
            self.time_elapsed = self.timer.elapsed() / 1000  # segundos
            score = max(1, int(10000 / self.time_elapsed))  # inverso del tiempo
            prompt_player_name("mines", score)

    def show_message(self, text):
        self.message_label.setText(text)
        self.message_label.show()
        QTimer.singleShot(2000, self.message_label.hide)

    def check_win(self):
        for c in self.cells.values():
            if not c.is_mine and not c.is_revealed:
                return
        self.trigger_game_over(True)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "message_label") and hasattr(self, "play_area"):
        # Centra el mensaje dentro de la caja de juego
            w, h = 400, 100
            rect = self.play_area.geometry()
        x = rect.x() + rect.width() // 2 - w // 2
        y = rect.y() + rect.height() // 2 - h // 2
        self.message_label.setGeometry(x, y, w, h)


    def back_to_menu(self):
        if self.stacked_widget:
            self.stacked_widget.setCurrentIndex(0)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

    # Fondo CRT negro con líneas verdes
        painter.fillRect(self.rect(), QColor(0, 0, 0))
        pen = QPen(QColor(0, 40, 60))  # líneas celeste oscuro
        for y in range(0, self.height(), 4):
            painter.setPen(pen)
            painter.drawLine(0, y, self.width(), y)

