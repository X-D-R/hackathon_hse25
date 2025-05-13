import cProfile
import pstats
from pstats import SortKey
from memory_profiler import profile
import time
import pandas as pd
from typing import Callable
import os
import matplotlib.pyplot as plt
import seaborn as sns


class Profiler:
    """
    Класс для профилирования времени выполнения и использования памяти
    """

    def __init__(self, output_dir: str = "profiling_results"):
        self.output_dir = output_dir
        self.profiler = cProfile.Profile()
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "graphics"), exist_ok=True)

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

            time_profile_path = os.path.join(self.output_dir, "profiling_time.txt")
            print('=' * 50)
            print(f"Функция {func.__name__} выполнилась за {overall_time:.4f} секунд")
            with open(time_profile_path, "w") as f:
                stats = pstats.Stats(self.profiler, stream=f)
                stats.sort_stats(SortKey.TIME)
                stats.print_stats()
                print(f"Результаты профилирования сохранены в {time_profile_path}")
            print('=' * 50)
            self.plot_time_stats(stats)
            return result

        return wrapper

    def plot_time_stats(self, stats: pstats.Stats):
        """Генерирует график по результатам профилирования времени"""
        stats.sort_stats(SortKey.TIME)
        data = []
        for func, (cc, nc, tt, ct, callers) in stats.stats.items():
            file, line, name = func
            data.append({
                'function': f"{file}:{line}({name})",
                'total_time': tt,
                'cumulative_time': ct,
                'call_count': nc
            })

        df = pd.DataFrame(data).sort_values('total_time', ascending=False).head(10)

        plt.figure(figsize=(12, 6))
        sns.barplot(x='total_time', y='function', data=df)
        plt.title(f"Top 10 Time Consumers")
        plt.xlabel("Total Time (seconds)")
        plt.ylabel("Function")

        plot_path = os.path.join(self.output_dir, "graphics", f"profiling_time.png")
        plt.tight_layout()
        plt.savefig(plot_path)
        plt.close()
        print(f"График профилирования времени сохранен в {plot_path}")

    def profile_memory(self, func: Callable) -> Callable:
        """
        Декоратор для профилирования использования памяти

        :param func: Функция для профилирования
        :return: Обернутая функция
        """
        memory_profile_path = os.path.join(self.output_dir, "profiling_memory.txt")
        fp = open(memory_profile_path, 'w+')

        @profile(stream=fp)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            return result

        return wrapper

    def run_with_profiling(self, func: Callable, *args, **kwargs):
        """
        Запуск функции с полным профилированием (время + память)

        :param func: Функция для выполнения и профилирования
        """
        decorated_func = self.profile_time(self.profile_memory(func))
        return decorated_func(*args, **kwargs)

    def run_with_time_profiling(self, func: Callable, *args, **kwargs):
        """
        Запуск функции с полным профилированием (время + память)

        :param func: Функция для выполнения и профилирования
        """
        decorated_func = self.profile_time(func)
        return decorated_func(*args, **kwargs)

    def run_with_memory_profiling(self, func: Callable, *args, **kwargs):
        """
        Запуск функции с полным профилированием (время + память)

        :param func: Функция для выполнения и профилирования
        """
        decorated_func = self.profile_memory(func)
        return decorated_func(*args, **kwargs)
