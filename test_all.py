"""
Все тесты для проекта KursPy
"""
import unittest
from graph import floyd_warshall
from matrix import matrix_multiplication, generate_matrix
from sort import bubble_sort, selection_sort, compare_sorts, generate_test_data


# ============================================================================
# ТЕСТЫ ДЛЯ ГРАФОВ (Floyd-Warshall)
# ============================================================================

class TestFloydWarshall(unittest.TestCase):
    """Тесты для алгоритма Флойда-Уоршелла"""
    
    def test_simple_graph(self):
        """Тест простого графа из 3 вершин"""
        graph = [
            [0, 1, 4],
            [1, 0, 2],
            [4, 2, 0]
        ]
        dist, comparisons, time_taken = floyd_warshall(graph)
        
        self.assertEqual(dist[0][0], 0)
        self.assertEqual(dist[1][1], 0)
        self.assertEqual(dist[2][2], 0)
        self.assertEqual(dist[0][1], 1)
        self.assertEqual(dist[1][2], 2)
        self.assertEqual(dist[0][2], 3)
        self.assertGreaterEqual(time_taken, 0)
        self.assertGreater(comparisons, 0)
    
    def test_disconnected_graph(self):
        """Тест графа с несвязанными вершинами"""
        graph = [
            [0, 1, 0],
            [1, 0, 0],
            [0, 0, 0]
        ]
        dist, comparisons, time_taken = floyd_warshall(graph)
        
        self.assertEqual(dist[0][2], float('inf'))
        self.assertEqual(dist[2][0], float('inf'))
        self.assertEqual(dist[1][2], float('inf'))
        self.assertEqual(dist[2][1], float('inf'))
        self.assertEqual(dist[0][1], 1)
        self.assertEqual(dist[1][0], 1)
    
    def test_single_vertex(self):
        """Тест графа с одной вершиной"""
        graph = [[0]]
        dist, comparisons, time_taken = floyd_warshall(graph)
        
        self.assertEqual(dist[0][0], 0)
        self.assertEqual(len(dist), 1)
        self.assertEqual(len(dist[0]), 1)
    
    def test_complete_graph(self):
        """Тест полного графа"""
        graph = [
            [0, 1, 2, 3],
            [1, 0, 4, 5],
            [2, 4, 0, 6],
            [3, 5, 6, 0]
        ]
        dist, comparisons, time_taken = floyd_warshall(graph)
        
        for i in range(4):
            self.assertEqual(dist[i][i], 0)
        for i in range(4):
            for j in range(4):
                self.assertNotEqual(dist[i][j], float('inf'))
    
    def test_large_graph(self):
        """Тест большого графа"""
        n = 10
        graph = [[0 if i == j else 1 for j in range(n)] for i in range(n)]
        dist, comparisons, time_taken = floyd_warshall(graph)
        
        self.assertEqual(len(dist), n)
        self.assertEqual(len(dist[0]), n)
        for i in range(n):
            self.assertEqual(dist[i][i], 0)
    
    def test_return_types(self):
        """Тест типов возвращаемых значений"""
        graph = [[0, 1], [1, 0]]
        dist, comparisons, time_taken = floyd_warshall(graph)
        
        self.assertIsInstance(dist, list)
        self.assertIsInstance(comparisons, int)
        self.assertIsInstance(time_taken, float)
        self.assertEqual(len(dist), 2)
        self.assertEqual(len(dist[0]), 2)


# ============================================================================
# ТЕСТЫ ДЛЯ МАТРИЦ
# ============================================================================

class TestMatrixMultiplication(unittest.TestCase):
    """Тесты для умножения матриц"""
    
    def test_square_matrices(self):
        """Тест умножения квадратных матриц"""
        A = [[1, 2], [3, 4]]
        B = [[5, 6], [7, 8]]
        result, comparisons, time_taken = matrix_multiplication(A, B)
        
        self.assertEqual(result[0][0], 19)
        self.assertEqual(result[0][1], 22)
        self.assertEqual(result[1][0], 43)
        self.assertEqual(result[1][1], 50)
        self.assertGreater(comparisons, 0)
        self.assertGreaterEqual(time_taken, 0)
    
    def test_rectangular_matrices(self):
        """Тест умножения прямоугольных матриц"""
        A = [[1, 2, 3], [4, 5, 6]]
        B = [[7, 8], [9, 10], [11, 12]]
        result, comparisons, time_taken = matrix_multiplication(A, B)
        
        self.assertEqual(len(result), 2)
        self.assertEqual(len(result[0]), 2)
        self.assertEqual(result[0][0], 58)
        self.assertEqual(result[0][1], 64)
        self.assertEqual(result[1][0], 139)
        self.assertEqual(result[1][1], 154)
    
    def test_identity_matrix(self):
        """Тест умножения на единичную матрицу"""
        A = [[1, 2, 3], [4, 5, 6]]
        I = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
        result, comparisons, time_taken = matrix_multiplication(A, I)
        self.assertEqual(result, A)
    
    def test_zero_matrix(self):
        """Тест умножения на нулевую матрицу"""
        A = [[1, 2], [3, 4]]
        Z = [[0, 0], [0, 0]]
        result, comparisons, time_taken = matrix_multiplication(A, Z)
        self.assertEqual(result, [[0, 0], [0, 0]])
    
    def test_single_element(self):
        """Тест умножения матриц 1x1"""
        A = [[5]]
        B = [[3]]
        result, comparisons, time_taken = matrix_multiplication(A, B)
        self.assertEqual(result, [[15]])
    
    def test_incompatible_dimensions(self):
        """Тест умножения несовместимых матриц"""
        A = [[1, 2], [3, 4]]
        B = [[5, 6, 7]]
        with self.assertRaises(ValueError):
            matrix_multiplication(A, B)
    
    def test_return_types(self):
        """Тест типов возвращаемых значений"""
        A = [[1, 2], [3, 4]]
        B = [[5, 6], [7, 8]]
        result, comparisons, time_taken = matrix_multiplication(A, B)
        self.assertIsInstance(result, list)
        self.assertIsInstance(comparisons, int)
        self.assertIsInstance(time_taken, float)
    
    def test_large_matrices(self):
        """Тест умножения больших матриц"""
        A = [[1] * 10 for _ in range(5)]
        B = [[1] * 3 for _ in range(10)]
        result, comparisons, time_taken = matrix_multiplication(A, B)
        
        self.assertEqual(len(result), 5)
        self.assertEqual(len(result[0]), 3)
        self.assertEqual(result[0][0], 10)


class TestGenerateMatrix(unittest.TestCase):
    """Тесты для генерации матриц"""
    
    def test_square_matrix(self):
        """Тест генерации квадратной матрицы"""
        matrix = generate_matrix(3)
        self.assertEqual(len(matrix), 3)
        self.assertEqual(len(matrix[0]), 3)
    
    def test_rectangular_matrix(self):
        """Тест генерации прямоугольной матрицы"""
        matrix = generate_matrix(2, 4)
        self.assertEqual(len(matrix), 2)
        self.assertEqual(len(matrix[0]), 4)
    
    def test_matrix_values(self):
        """Тест диапазона значений в матрице"""
        matrix = generate_matrix(5, 5)
        for row in matrix:
            for val in row:
                self.assertGreaterEqual(val, 1)
                self.assertLessEqual(val, 10)
                self.assertIsInstance(val, int)
    
    def test_single_element(self):
        """Тест генерации матрицы 1x1"""
        matrix = generate_matrix(1, 1)
        self.assertEqual(len(matrix), 1)
        self.assertEqual(len(matrix[0]), 1)
        self.assertGreaterEqual(matrix[0][0], 1)
        self.assertLessEqual(matrix[0][0], 10)
    
    def test_large_matrix(self):
        """Тест генерации большой матрицы"""
        matrix = generate_matrix(10, 15)
        self.assertEqual(len(matrix), 10)
        self.assertEqual(len(matrix[0]), 15)
        for row in matrix:
            self.assertEqual(len(row), 15)


# ============================================================================
# ТЕСТЫ ДЛЯ СОРТИРОВКИ
# ============================================================================

class TestBubbleSort(unittest.TestCase):
    """Тесты для сортировки пузырьком"""
    
    def test_simple_sort(self):
        arr = [3, 1, 4, 1, 5, 9, 2, 6]
        sorted_arr, comparisons, time_taken = bubble_sort(arr)
        self.assertEqual(sorted_arr, [1, 1, 2, 3, 4, 5, 6, 9])
        self.assertGreater(comparisons, 0)
        self.assertEqual(arr, [3, 1, 4, 1, 5, 9, 2, 6])
    
    def test_already_sorted(self):
        arr = [1, 2, 3, 4, 5]
        sorted_arr, comparisons, time_taken = bubble_sort(arr)
        self.assertEqual(sorted_arr, [1, 2, 3, 4, 5])
    
    def test_reverse_sorted(self):
        arr = [5, 4, 3, 2, 1]
        sorted_arr, comparisons, time_taken = bubble_sort(arr)
        self.assertEqual(sorted_arr, [1, 2, 3, 4, 5])
    
    def test_single_element(self):
        arr = [42]
        sorted_arr, comparisons, time_taken = bubble_sort(arr)
        self.assertEqual(sorted_arr, [42])
    
    def test_empty_array(self):
        arr = []
        sorted_arr, comparisons, time_taken = bubble_sort(arr)
        self.assertEqual(sorted_arr, [])
    
    def test_duplicates(self):
        arr = [3, 3, 3, 1, 1, 2, 2]
        sorted_arr, comparisons, time_taken = bubble_sort(arr)
        self.assertEqual(sorted_arr, [1, 1, 2, 2, 3, 3, 3])
    
    def test_negative_numbers(self):
        arr = [-3, -1, -5, 2, 0, -2]
        sorted_arr, comparisons, time_taken = bubble_sort(arr)
        self.assertEqual(sorted_arr, [-5, -3, -2, -1, 0, 2])


class TestSelectionSort(unittest.TestCase):
    """Тесты для сортировки выбором"""
    
    def test_simple_sort(self):
        arr = [3, 1, 4, 1, 5, 9, 2, 6]
        sorted_arr, comparisons, time_taken = selection_sort(arr)
        self.assertEqual(sorted_arr, [1, 1, 2, 3, 4, 5, 6, 9])
        self.assertGreater(comparisons, 0)
        self.assertEqual(arr, [3, 1, 4, 1, 5, 9, 2, 6])
    
    def test_already_sorted(self):
        arr = [1, 2, 3, 4, 5]
        sorted_arr, comparisons, time_taken = selection_sort(arr)
        self.assertEqual(sorted_arr, [1, 2, 3, 4, 5])
    
    def test_reverse_sorted(self):
        arr = [5, 4, 3, 2, 1]
        sorted_arr, comparisons, time_taken = selection_sort(arr)
        self.assertEqual(sorted_arr, [1, 2, 3, 4, 5])
    
    def test_single_element(self):
        arr = [42]
        sorted_arr, comparisons, time_taken = selection_sort(arr)
        self.assertEqual(sorted_arr, [42])
    
    def test_empty_array(self):
        arr = []
        sorted_arr, comparisons, time_taken = selection_sort(arr)
        self.assertEqual(sorted_arr, [])
    
    def test_duplicates(self):
        arr = [3, 3, 3, 1, 1, 2, 2]
        sorted_arr, comparisons, time_taken = selection_sort(arr)
        self.assertEqual(sorted_arr, [1, 1, 2, 2, 3, 3, 3])
    
    def test_negative_numbers(self):
        arr = [-3, -1, -5, 2, 0, -2]
        sorted_arr, comparisons, time_taken = selection_sort(arr)
        self.assertEqual(sorted_arr, [-5, -3, -2, -1, 0, 2])


class TestCompareSorts(unittest.TestCase):
    """Тесты для функции сравнения сортировок"""
    
    def test_compare_sorts(self):
        arr = [3, 1, 4, 1, 5, 9, 2, 6]
        results = compare_sorts(arr)
        
        self.assertIn("Пузырьковая", results)
        self.assertIn("Выбором", results)
        
        expected = [1, 1, 2, 3, 4, 5, 6, 9]
        self.assertEqual(results["Пузырьковая"]["sorted_array"], expected)
        self.assertEqual(results["Выбором"]["sorted_array"], expected)
        
        for name, data in results.items():
            self.assertIn("sorted_array", data)
            self.assertIn("comparisons", data)
            self.assertIn("time", data)
            self.assertIsInstance(data["comparisons"], int)
            self.assertIsInstance(data["time"], float)
            self.assertGreaterEqual(data["time"], 0)
    
    def test_empty_array(self):
        arr = []
        results = compare_sorts(arr)
        for name, data in results.items():
            self.assertEqual(data["sorted_array"], [])
    
    def test_single_element(self):
        arr = [42]
        results = compare_sorts(arr)
        for name, data in results.items():
            self.assertEqual(data["sorted_array"], [42])


class TestGenerateTestData(unittest.TestCase):
    """Тесты для генерации тестовых данных"""
    
    def test_default_size(self):
        data = generate_test_data()
        self.assertEqual(len(data), 100)
        for val in data:
            self.assertGreaterEqual(val, 1)
            self.assertLessEqual(val, 1000)
            self.assertIsInstance(val, int)
    
    def test_custom_size(self):
        data = generate_test_data(50)
        self.assertEqual(len(data), 50)
    
    def test_small_size(self):
        data = generate_test_data(1)
        self.assertEqual(len(data), 1)
        self.assertGreaterEqual(data[0], 1)
        self.assertLessEqual(data[0], 1000)
    
    def test_large_size(self):
        data = generate_test_data(1000)
        self.assertEqual(len(data), 1000)
        for i in range(0, 1000, 100):
            self.assertGreaterEqual(data[i], 1)
            self.assertLessEqual(data[i], 1000)


class TestAllSortsConsistency(unittest.TestCase):
    """Тесты на согласованность всех алгоритмов сортировки"""
    
    def test_all_sorts_same_result(self):
        """Тест, что все алгоритмы дают одинаковый результат"""
        test_cases = [
            [3, 1, 4, 1, 5, 9, 2, 6],
            [1, 2, 3, 4, 5],
            [5, 4, 3, 2, 1],
            [1],
            [],
            [3, 3, 3, 1, 1, 2, 2],
            [-3, -1, -5, 2, 0, -2]
        ]
        
        for arr in test_cases:
            bubble_result, _, _ = bubble_sort(arr)
            selection_result, _, _ = selection_sort(arr)
            
            self.assertEqual(bubble_result, selection_result,
                           f"Bubble и Selection дали разные результаты для {arr}")


# ============================================================================
# ЗАПУСК ВСЕХ ТЕСТОВ
# ============================================================================

if __name__ == '__main__':
    unittest.main(verbosity=2)
