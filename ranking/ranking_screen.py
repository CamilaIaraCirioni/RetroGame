from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint, QTimer
from PyQt5.QtGui import QFont, QLinearGradient, QBrush, QColor, QPalette
from ranking.ranking_manager import get_top_scores

class RankingScreen(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.current_game = "snake"
        self.init_ui()

    def init_ui(self):
        # Fondo retro dorado CRT
        palette = QPalette()
        gradient = QLinearGradient(0, 0, 0, 1)
        gradient.setCoordinateMode(QLinearGradient.ObjectBoundingMode)
        gradient.setColorAt(0.0, QColor("#1a1a00"))
        gradient.setColorAt(1.0, QColor("#000000"))
        palette.setBrush(QPalette.Window, QBrush(gradient))
        self.setAutoFillBackground(True)
        self.setPalette(palette)

        #  Título
        self.title = QLabel("🏆 RANKING 🏆")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setFont(QFont("Courier New", 38, QFont.Bold))
        self.title.setStyleSheet("""
            QLabel {
                color: #FFD700;
                text-shadow: 0 0 15px #FFFF66, 0 0 30px #FFD700;
            }
        """)

        # Botones
        self.btn_snake = self.create_button("🐍 SNAKE", lambda: self.show_game("snake"))
        self.btn_mines = self.create_button("💣 MINES", lambda: self.show_game("mines"))
        self.btn_pong = self.create_button("🏓 PONG", lambda: self.show_game("pong"))
        self.btn_back = self.create_button("⬅ VOLVER", lambda: self.stacked_widget.setCurrentIndex(0))

        game_buttons = QHBoxLayout()
        for b in [self.btn_snake, self.btn_mines, self.btn_pong]:
            game_buttons.addWidget(b)
        game_buttons.addStretch()
        game_buttons.addWidget(self.btn_back)

        # Tabla
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Jugador", "Puntaje", "Fecha"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(True)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: rgba(20, 20, 0, 220);
                color: #FFD700;
                gridline-color: #FFFF33;
                border: 2px solid #FFD700;
                selection-background-color: #FFD700;
                selection-color: black;
                font-family: 'Courier New';
                font-size: 16px;
            }
            QHeaderView::section {
                background-color: #222200;
                color: #FFD700;
                border: none;
                font-weight: bold;
                font-size: 18px;
            }
        """)

        layout = QVBoxLayout()
        layout.addWidget(self.title)
        layout.addLayout(game_buttons)
        layout.addWidget(self.table)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(25)
        self.setLayout(layout)

        self.show_game("snake")

    def create_button(self, text, func):
        btn = QPushButton(text)
        btn.setFixedSize(170, 45)
        btn.clicked.connect(func)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(30, 30, 0, 180);
                color: #FFD700;
                border: 2px solid #FFD700;
                border-radius: 10px;
                font-family: 'Courier New';
                font-weight: bold;
                letter-spacing: 1px;
            }
            QPushButton:hover {
                background-color: #FFD700;
                color: #000;
            }
            QPushButton:pressed {
                background-color: #FFFF66;
                color: #000;
            }
        """)
        return btn

    def show_game(self, game):
        self.current_game = game
        self.update_table()

        anim = QPropertyAnimation(self.table, b"pos")
        anim.setDuration(600)
        anim.setStartValue(self.table.pos() + QPoint(0, 80))
        anim.setEndValue(self.table.pos())
        anim.setEasingCurve(QEasingCurve.OutBounce)
        anim.start()
        self.anim = anim

        QTimer.singleShot(150, lambda: self.title.setStyleSheet("""
            QLabel {
                color: #FFD700;
                text-shadow: 0 0 15px #FFFF66, 0 0 30px #FFD700;
            }
        """))

    def update_table(self):
        data = get_top_scores(self.current_game)
        self.table.setRowCount(len(data))
        for i, entry in enumerate(data):
            self.table.setItem(i, 0, QTableWidgetItem(entry["player"]))
            self.table.setItem(i, 1, QTableWidgetItem(str(entry["score"])))
            self.table.setItem(i, 2, QTableWidgetItem(entry["date"]))
