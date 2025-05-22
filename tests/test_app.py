import unittest

class BrightBitsLogic:
    """Допоміжний клас для тестування логіки перетворення"""

    @staticmethod
    def decimal_to_binary(n):
        return bin(n)[2:].zfill(8)

    @staticmethod
    def binary_to_decimal(bstr):
        return int(bstr, 2)


class TestBrightBits(unittest.TestCase):

    def test_decimal_to_binary(self):
        self.assertEqual(BrightBitsLogic.decimal_to_binary(0), '00000000')
        self.assertEqual(BrightBitsLogic.decimal_to_binary(5), '00000101')
        self.assertEqual(BrightBitsLogic.decimal_to_binary(255), '11111111')
        self.assertEqual(BrightBitsLogic.decimal_to_binary(13), '00001101')

    def test_binary_to_decimal(self):
        self.assertEqual(BrightBitsLogic.binary_to_decimal('00000000'), 0)
        self.assertEqual(BrightBitsLogic.binary_to_decimal('00000101'), 5)
        self.assertEqual(BrightBitsLogic.binary_to_decimal('11111111'), 255)
        self.assertEqual(BrightBitsLogic.binary_to_decimal('00001101'), 13)

    def test_bidirectional_conversion(self):
        for num in range(256):
            binary = BrightBitsLogic.decimal_to_binary(num)
            self.assertEqual(BrightBitsLogic.binary_to_decimal(binary), num)


if __name__ == '__main__':
    unittest.main()
