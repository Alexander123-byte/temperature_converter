import unittest
from temperature_converter import TemperatureConverter


class TestTemperatureConverter(unittest.TestCase):
    def test_celsius_to_fahrenheit(self):
        # Тестируем обычные значения
        self.assertAlmostEqual(TemperatureConverter.c_to_f(0), 32)
        self.assertAlmostEqual(TemperatureConverter.c_to_f(100), 212)
        self.assertAlmostEqual(TemperatureConverter.c_to_f(-40), -40)  # Особый случай
        self.assertAlmostEqual(TemperatureConverter.c_to_f(37.5), 99.5)  # Дробные значения

    def test_fahrenheit_to_celsius(self):
        # Тестируем обычные значения
        self.assertAlmostEqual(TemperatureConverter.f_to_c(32), 0)
        self.assertAlmostEqual(TemperatureConverter.f_to_c(212), 100)
        self.assertAlmostEqual(TemperatureConverter.f_to_c(-40), -40)  # Особый случай
        self.assertAlmostEqual(TemperatureConverter.f_to_c(99.5), 37.5)  # Дробные значения

    def test_absolute_zero_checks(self):
        # Проверяем обработку температур ниже абсолютного нуля
        with self.assertRaises(ValueError):
            TemperatureConverter.c_to_f(-274)  # Ниже -273.15°C

        with self.assertRaises(ValueError):
            TemperatureConverter.f_to_c(-460)  # Ниже -459.67°F

    def test_boundary_values(self):
        # Проверка граничных допустимых значений
        self.assertAlmostEqual(TemperatureConverter.f_to_c(-459.67), -273.15)
        self.assertAlmostEqual(TemperatureConverter.c_to_f(-273.15), -459.67)


if __name__ == '__main__':
    unittest.main()
