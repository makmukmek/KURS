import time
import random

def bubble_sort(arr):
    """Сортировка пузырьком O(n²)"""
    comparisons = 0
    start_time = time.time()
    
    n = len(arr)
    arr_copy = arr.copy()
    
    for i in range(n):
        for j in range(0, n-i-1):
            comparisons += 1
            if arr_copy[j] > arr_copy[j+1]:
                arr_copy[j], arr_copy[j+1] = arr_copy[j+1], arr_copy[j]
    
    time_taken = time.time() - start_time
    return arr_copy, comparisons, time_taken

def selection_sort(arr):
    """Сортировка выбором O(n²)"""
    comparisons = 0
    start_time = time.time()
    
    arr_copy = arr.copy()
    n = len(arr_copy)
    
    for i in range(n):
        min_idx = i
        for j in range(i+1, n):
            comparisons += 1
            if arr_copy[j] < arr_copy[min_idx]:
                min_idx = j
        
        arr_copy[i], arr_copy[min_idx] = arr_copy[min_idx], arr_copy[i]
    
    time_taken = time.time() - start_time
    return arr_copy, comparisons, time_taken

def compare_sorts(arr):
    """Сравнение всех алгоритмов сортировки"""
    results = {}
    
    # Тестируем каждый алгоритм
    algorithms = [
        ("Пузырьковая", bubble_sort),
        ("Выбором", selection_sort)
    ]
    
    for name, algorithm in algorithms:
        sorted_arr, comparisons, time_taken = algorithm(arr)
        results[name] = {
            'sorted_array': sorted_arr,
            'comparisons': comparisons,
            'time': time_taken
        }
    
    return results

def generate_test_data(size=100):
    """Генерация тестовых данных"""
    return [random.randint(1, 1000) for _ in range(size)]