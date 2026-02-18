import time
def floyd_warshall(graph):
    """Алгоритм Флойда-Уоршелла n**3"""
    comparisons = 0
    start_time = time.time()
    
    n = len(graph)
    dist = [[float('inf')] * n for _ in range(n)]
    
    # Инициализация матрицы расстояний
    for i in range(n):
        for j in range(n):
            comparisons += 1
            if i == j:
                dist[i][j] = 0
            elif graph[i][j] != 0:
                dist[i][j] = graph[i][j]
    
    # Основной алгоритм
    for k in range(n):
        for i in range(n):
            for j in range(n):
                comparisons += 1
                if dist[i][j] > dist[i][k] + dist[k][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
    
    time_taken = time.time() - start_time
    return dist, comparisons, time_taken