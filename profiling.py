import cProfile
import pstats
from pstats import SortKey
from memory_profiler import profile
import time
import pandas as pd
from typing import Callable


class Profiler:
    """
    Класс для профилирования времени выполнения и использования памяти
    """

    def __init__(self, output_file: str = None):
        self.output_file = output_file
        self.profiler = cProfile.Profile()

    def profile_time(self, func: Callable) -> Callable:
        """
        Декоратор для профилирования времени выполнения

        :param func: Функция для профилирования
        :return: Обернутая функция
        """

        def wrapper(*args, **kwargs):
            self.profiler.enable()
            start_time = time.time()

            result = func(*args, **kwargs)

            end_time = time.time()
            self.profiler.disable()

            overall_time = end_time - start_time
            print('=' * 50)
            print(f"Функция {func.__name__} выполнилась за {overall_time:.4f} секунд")
            with open(f"{self.output_file}_time.txt", "w") as f:
                stats = pstats.Stats(self.profiler, stream=f)
                stats.sort_stats(SortKey.TIME)
                stats.print_stats()
                print(f"Результаты профилирования сохранены в {self.output_file}_time.txt")
            print('=' * 50)
            return result

        return wrapper

    def profile_memory(self, func: Callable) -> Callable:
        """
        Декоратор для профилирования использования памяти

        :param func: Функция для профилирования
        :return: Обернутая функция
        """

        with open(f"{self.output_file}_memory.txt", "w") as f:
            @profile(stream=f)
            def wrapper(*args, **kwargs):
                result = func(*args, **kwargs)
                return result
            print(f"Результаты профилирования сохранены в {self.output_file}_memory.txt")
            return wrapper
        return wrapper

    def run_with_profiling(self, func: Callable, *args, **kwargs):
        """
        Запуск функции с полным профилированием (время + память)

        :param func: Функция для выполнения и профилирования
        """
        decorated_func = self.profile_time(self.profile_memory(func))
        return decorated_func(*args, **kwargs)
