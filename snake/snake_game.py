from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QComboBox
from PyQt5.QtCore import Qt, QTimer, QRect, QPoint
from PyQt5.QtGui import QPainter, QColor, QFont, QPen, QBrush
from ranking.name_prompt import prompt_player_name
import random


class SnakeGame(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.setFocusPolicy(Qt.StrongFocus)
        self.setStyleSheet("background-color: black;")
        self.grid_size = 20
        self.flash_alpha = 0
        self.frame_color_value = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_game)
        self.play_area = QRect()  #  caja central del juego
        self.init_ui()
        self.reset_game()
        self.awaiting_start = True


    def init_ui(self):
        # Título
        self.title = QLabel("🕹️ SNAKE 1984", self)
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setFont(QFont("Courier New", 32, QFont.Bold))
        self.title.setStyleSheet("color: #00FF00; margin: 10px;")

        # Botones
        self.btn_restart = QPushButton("🔁 REINICIAR")
        self.btn_restart.setStyleSheet(self.button_style())
        self.btn_restart.setFixedSize(150, 40)
        self.btn_restart.clicked.connect(self.reset_game)

        self.btn_pause = QPushButton("⏸️ PAUSAR")
        self.btn_pause.setStyleSheet(self.button_style())
        self.btn_pause.setFixedSize(150, 40)
        self.btn_pause.clicked.connect(self.toggle_pause)

        self.btn_back = QPushButton("⬅ MENÚ")
        self.btn_back.setStyleSheet(self.button_style())
        self.btn_back.setFixedSize(150, 40)
        self.btn_back.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))

        # Dificultad
        self.difficulty_box = QComboBox()
        self.difficulty_box.addItems(["FÁCIL", "NORMAL", "DIFÍCIL"])
        self.difficulty_box.setStyleSheet("""
            QComboBox {
                color: #00FF00;
                background-color: #000;
                border: 1px solid #00FF00;
                font-family: 'Courier New';
                font-size: 14px;
                padding: 4px;
            }
        """)
        self.difficulty_box.currentIndexChanged.connect(self.change_difficulty)
        self.difficulty_box.setFocusPolicy(Qt.NoFocus)
        for w in [self.btn_restart, self.btn_pause, self.btn_back, self.difficulty_box]:
            w.setFocusPolicy(Qt.NoFocus)




        # Layout superior
        top_layout = QHBoxLayout()
        top_layout.addWidget(self.btn_restart)
        top_layout.addWidget(self.btn_pause)
        top_layout.addWidget(self.btn_back)
        top_layout.addStretch()
        top_layout.addWidget(QLabel("DIFICULTAD:", self))
        top_layout.addWidget(self.difficulty_box)

        # Layout principal
        layout = QVBoxLayout(self)
        layout.addWidget(self.title, alignment=Qt.AlignCenter)
        layout.addLayout(top_layout)
        layout.addStretch()
        layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(layout)

    def button_style(self):
        return """
            QPushButton {
                background-color: #111;
                color: #00FF00;
                border: 2px solid #00FF00;
                border-radius: 6px;
                font-family: 'Courier New';
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #00FF00;
                color: black;
            }
        """

    def reset_game(self):
        self.snake = [QPoint(5, 5)]
        self.direction = QPoint(1, 0)
        self.score = 0
        self.game_over = False
        self.paused = False

    # Mantener la dificultad ya seleccionada
        level = self.difficulty_box.currentText()
        if level == "FÁCIL":
            self.speed = 150
        elif level == "NORMAL":
            self.speed = 100
        else:
            self.speed = 70

        self.timer.stop()
        self.awaiting_start = True

    # Comida
        if self.play_area.width() > 0:
            self.spawn_food()
        else:
            self.food = None

        self.update()
        QTimer.singleShot(0, lambda: self.setFocus(Qt.TabFocusReason))



    def change_difficulty(self):
        level = self.difficulty_box.currentText()
        if level == "FÁCIL":
            self.speed = 150
        elif level == "NORMAL":
            self.speed = 100
        else:
            self.speed = 70
        if not self.awaiting_start and not self.paused:
            self.timer.start(self.speed)


    def toggle_pause(self):
        if self.paused:
            self.timer.start(self.speed)
            self.btn_pause.setText("⏸️ PAUSAR")
        else:
            self.timer.stop()
            self.btn_pause.setText("▶️ REANUDAR")
        self.paused = not self.paused

    def spawn_food(self):
    # Evita errores si el área aún no está definida
        if not hasattr(self, "play_area") or self.play_area.width() <= 0:
            return

        cols = self.play_area.width() // self.grid_size
        rows = self.play_area.height() // self.grid_size

        while True:
            fx = random.randint(0, cols - 1)
            fy = random.randint(0, rows - 1)
            pos = QPoint(fx, fy)
            if pos not in self.snake:
                self.food = pos
                break


    def keyPressEvent(self, event):
        if self.game_over:
            return

        key = event.key()

        if self.awaiting_start:
            self.awaiting_start = False
            self.timer.start(self.speed)

        if key == Qt.Key_1:
            self.difficulty_box.setCurrentIndex(0)
            return
        elif key == Qt.Key_2:
            self.difficulty_box.setCurrentIndex(1)
            return
        elif key == Qt.Key_3:
            self.difficulty_box.setCurrentIndex(2)
            return

        #Arriba
        if key in (Qt.Key_Up, Qt.Key_W) and self.direction != QPoint(0, 1):
            self.direction = QPoint(0, -1)

    # abajo
        elif key in (Qt.Key_Down, Qt.Key_S) and self.direction != QPoint(0, -1):
            self.direction = QPoint(0, 1)

    # izq
        elif key in (Qt.Key_Left, Qt.Key_A) and self.direction != QPoint(1, 0):
            self.direction = QPoint(-1, 0)

    # der
        elif key in (Qt.Key_Right, Qt.Key_D, Qt.Key_D) and self.direction != QPoint(-1, 0):
            self.direction = QPoint(1, 0)

    # pausa
        elif key == Qt.Key_Space:
            self.toggle_pause()


    def update_game(self):
        if self.game_over or self.paused:
            return

        head = self.snake[0] + self.direction
        cols = self.play_area.width() // self.grid_size
        rows = self.play_area.height() // self.grid_size

        # Colisiones con bordes del área delimitada
        if head.x() < 0 or head.y() < 0 or head.x() >= cols or head.y() >= rows or head in self.snake:
            self.timer.stop()
            self.game_over = True
            self.setFocus(Qt.TabFocusReason)

            self.update()

    
            score = self.score
            QTimer.singleShot(1200, lambda: prompt_player_name("snake", score))
            return

        self.snake.insert(0, head)

        if head == self.food:
            self.score += 1
            self.flash_alpha = 18
            self.spawn_food()
        else:
            self.snake.pop()

        self.update()

    def resizeEvent(self, event):
    # Centrar el área de juego en la ventana
        box_width = 600
        box_height = 400
        x = (self.width() - box_width) // 2
        y = (self.height() - box_height) // 2 + 50
        self.play_area = QRect(x, y, box_width, box_height)

    # Crear comida si aún no existe
        if not hasattr(self, "food") or self.food is None:
            self.spawn_food()

        self.update()


    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Fondo CRT
        painter.fillRect(self.rect(), QColor(0, 0, 0))
        pen = QPen(QColor(0, 50, 0))
        for y in range(0, self.height(), 4):
            painter.setPen(pen)
            painter.drawLine(0, y, self.width(), y)
            
        self.frame_color_value = (self.frame_color_value + 1) % 255
        glow = abs(128 - self.frame_color_value) + 127
        painter.setPen(QPen(QColor(0, glow, 0), 3))

        # Área de juego (borde verde)
        painter.setPen(QPen(QColor("#00FF00"), 3))
        painter.drawRect(self.play_area)

        # Fondo interno de la caja
        inner_rect = self.play_area.adjusted(2, 2, -2, -2)
        painter.fillRect(inner_rect, QColor(0, 10, 0))

        # Dibujar comida
        painter.setBrush(QColor("#FF00FF"))
        fx = self.play_area.left() + self.food.x() * self.grid_size
        fy = self.play_area.top() + self.food.y() * self.grid_size
        painter.drawRect(fx, fy, self.grid_size, self.grid_size)
        
        if self.flash_alpha > 0:
            painter.fillRect(inner_rect, QColor(0, 255, 0, self.flash_alpha))
            self.flash_alpha = max(0, self.flash_alpha - 20)
        
        # Dibujar serpiente
        for i, segment in enumerate(self.snake):
            sx = self.play_area.left() + segment.x() * self.grid_size
            sy = self.play_area.top() + segment.y() * self.grid_size
            brightness = 255 - min(i * 10, 180)
            painter.setBrush(QColor(0, brightness, 0))
            painter.setPen(Qt.NoPen)
            painter.drawRect(sx, sy, self.grid_size - 1, self.grid_size - 1)

        # Puntaje
        painter.setFont(QFont("Courier New", 18, QFont.Bold))
        painter.setPen(QColor("#00FF00"))
        painter.drawText(20, 80, f"PUNTAJE: {self.score:03d}")

        # Game Over
        if self.game_over:
            pen = QPen(QColor(50, 0, 0))
            painter.setFont(QFont("Courier New", 36, QFont.Bold))
            painter.setPen(QColor("#FF0000"))
            painter.drawText(self.play_area, Qt.AlignCenter, "💀 GAME OVER 💀")
        else:
            pen = QPen(QColor(0, 50, 0))