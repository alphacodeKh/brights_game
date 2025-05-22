import unittest
from brights_game import BrightBitsGame
import tkinter as tk

class TestBrightBitsGame(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()  # приховати вікно під час тестів
        self.game = BrightBitsGame(self.root)

    def tearDown(self):
        self.root.destroy()

    def test_initial_score(self):
        self.assertEqual(self.game.score, 0)

    def test_toggle_bulb(self):
        self.game.bulb_values = [0] * 8
        self.game.toggle_bulb(3)
        self.assertEqual(self.game.bulb_values[3], 1)
        self.game.toggle_bulb(3)
        self.assertEqual(self.game.bulb_values[3], 0)

    def test_generate_decimal_task(self):
        self.game.game_mode = "decimal_to_binary"
        self.game.generate_task()
        self.assertGreaterEqual(self.game.current_decimal, 1)
        self.assertTrue(self.game.current_binary.isdigit())

    def test_generate_binary_task(self):
        self.game.game_mode = "binary_to_decimal"
        self.game.generate_task()
        self.assertEqual(int(self.game.current_binary, 2), self.game.current_decimal)

if __name__ == '__main__':
    unittest.main()

