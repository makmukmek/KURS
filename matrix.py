import time
import random

def matrix_multiplication(A, B):
    """Умножение матриц O(n³) - полиномиальная сложность"""
    comparisons = 0
    start_time = time.time()
    
    # Проверка на пустые матрицы
    if not A or not B:
        raise ValueError("Матрицы не могут быть пустыми")
    
    rows_A = len(A)
    if rows_A == 0 or not A[0]:
        raise ValueError("Матрица A пуста")
    cols_A = len(A[0])
    
    rows_B = len(B)
    if rows_B == 0 or not B[0]:
        raise ValueError("Матрица B пуста")
    cols_B = len(B[0])
    
    # Проверка, что все строки имеют одинаковую длину
    for i in range(rows_A):
        if len(A[i]) != cols_A:
            raise ValueError(f"Строка {i} матрицы A имеет неправильную длину")
    for i in range(rows_B):
        if len(B[i]) != cols_B:
            raise ValueError(f"Строка {i} матрицы B имеет неправильную длину")
    
    # Проверка возможности умножения
    if cols_A != rows_B:
        raise ValueError(f"Нельзя умножить матрицу {rows_A}×{cols_A} на матрицу {rows_B}×{cols_B}")
    
    # Создаем результирующую матрицу заполненную нулями
    C = [[0 for _ in range(cols_B)] for _ in range(rows_A)]
    
    for i in range(rows_A):
        for j in range(cols_B):
            for k in range(cols_A):
                comparisons += 1
                C[i][j] += A[i][k] * B[k][j]
    
    time_taken = time.time() - start_time
    return C, comparisons, time_taken

def generate_matrix(rows, cols=None):
    """
    Генерация случайной матрицы
    
    Args:
        rows: количество строк
        cols: количество столбцов (если None, то cols = rows для квадратной матрицы)
    
    Returns:
        Список списков - матрица с случайными значениями от 1 до 10
    """
    if cols is None:
        cols = rows  # Квадратная матрица по умолчанию
    return [[random.randint(1, 10) for _ in range(cols)] for _ in range(rows)]