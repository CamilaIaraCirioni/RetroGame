from PyQt5.QtWidgets import QApplication, QStackedWidget
from menu import GameMenu
from snake.snake_game import SnakeGame
from minesweeper.minesweeper_game import RetroMinesweeper
from pong.pong_game import PongGame
from ranking.ranking_screen import RankingScreen
import sys


app = QApplication(sys.argv)
stack = QStackedWidget()

menu = GameMenu(stack)
snake = SnakeGame(stack)
minesweeper = RetroMinesweeper(stack)
ranking_screen = RankingScreen(stack)
pong = PongGame(stack)

stack.addWidget(menu)
stack.addWidget(snake)
stack.addWidget(minesweeper)
stack.addWidget(pong)
stack.addWidget(ranking_screen)

stack.showFullScreen()
sys.exit(app.exec_())

