from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from ranking.ranking_manager import add_score, get_top_scores

def prompt_player_name(game, score):
    # Ver si califica para el ranking
    top = get_top_scores(game)
    if len(top) >= 10 and score <= top[-1]["score"]:
        return  # no entra al top

    dialog = QDialog()
    dialog.setWindowTitle("🏆 Nuevo récord!")
    dialog.setStyleSheet("""
        QDialog { background-color: black; border: 2px solid #FFD700; }
        QLabel { color: #FFD700; font-family: 'Courier New'; font-size: 18px; }
        QLineEdit {
            background-color: #222;
            color: #FFD700;
            border: 1px solid #FFD700;
            font-family: 'Courier New';
            font-size: 16px;
            padding: 5px;
        }
        QPushButton {
            background-color: #FFD700;
            color: black;
            font-weight: bold;
            font-family: 'Courier New';
        }
        QPushButton:hover { background-color: #FFFF66; }
    """)

    label = QLabel(f"🎉 ¡Nuevo récord en {game.upper()}! 🎮\nTu puntaje: {score}")
    name_input = QLineEdit()
    name_input.setPlaceholderText("Ingresa tu nombre...")

    btn = QPushButton("Guardar")
    btn.clicked.connect(dialog.accept)

    layout = QVBoxLayout()
    layout.addWidget(label, alignment=Qt.AlignCenter)
    layout.addWidget(name_input)
    layout.addWidget(btn, alignment=Qt.AlignCenter)
    dialog.setLayout(layout)

    if dialog.exec_() == QDialog.Accepted and name_input.text().strip():
        add_score(game, name_input.text().strip(), score)
