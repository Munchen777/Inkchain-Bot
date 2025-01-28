import openpyxl
import os
import sys

from collections import defaultdict, deque
from better_proxy import Proxy
from typing import DefaultDict, Dict, Deque, List, Set

from generall_settings import EXCEL_FILE_PATH
from modules import Logger
from openpyxl.utils.exceptions import InvalidFileException


logger: Logger = Logger().get_logger()


def get_accounts_data():
    try:
        try:
            workbook = openpyxl.load_workbook(EXCEL_FILE_PATH, read_only=True)
            sheet = workbook.active

        except InvalidFileException as error:
            logger.critical(f"Error for trying to open a non-ooxml file. Error {error}")
            sys.exit(1)

        except FileNotFoundError as error:
            logger.error("The file accounts.xlsx was not found")
            return

        except IsADirectoryError as error:
            logger.critical("Are you sure about excel file? Please, pass an excel file")
            sys.exit(1)

        account_names, private_keys, proxies, name_znc_domen = [], [], [], []

        for row in sheet.iter_rows(min_row=2):
            account_name = row[0].value
            private_key = row[1].value
            proxy = row[2].value
            name_znc_domen_value = row[3].value if len(row) == 4 else None

            if not all([account_name, private_key, proxy]):
                continue

            account_names.append(str(account_name) if isinstance(account_name, (str, int)) else None)
            private_keys.append(private_key if private_key else None)
            proxies.append(
                Proxy.from_str(
                    proxy=proxy.strip() if "://" in proxy.strip() else f"http://{proxy.strip()}"
                ).as_url
                if isinstance(proxy, str) else None
            )
            name_znc_domen.append(name_znc_domen_value if name_znc_domen_value else None)

        return account_names, private_keys, proxies, name_znc_domen

    except Exception as error:
        logger.error(f"Error in get_accounts_data function! Error: {error}")
        sys.exit(1)


def clean_progress_file():
    """
    Function to clean wallets progress file

    """
    with open("./data/service/wallets_progress.json", "w") as file:
        file.truncate(0)


def check_progress_file() -> bool:
    """
    Check if wallets_progress file is empty

    """
    file_path = './data/services/wallets_progress.json'

    if os.path.getsize(file_path) > 0:
        return True
    else:
        return False


# def topological_sort(graph: Dict[str, List[str]]) -> List[str]:
#     visited: Set[str] = set()
#     stack: List[str] = []

#     def dfs(module_name: str):
#         visited.add(module_name)

#         for neighbour in graph.get(module_name, []):
#             if neighbour not in visited:
#                 dfs(neighbour)

#         stack.append(module_name)

#     for module_name in graph:
#         if module_name not in visited:
#             dfs(module_name)

#     return stack[::-1]

# def remove_cycle(graph: DefaultDict[str, list[str]]):
#     for key, value in graph.items():
#         for neighbour in graph.get(key, []):
#             remove_edge()


def find_cycle(graph: DefaultDict[str, List[str]]) -> List[str] | None:
    visited: Set[str] = set()
    stack: Set[str] = set()

    def dfs(node: str, path: List) -> List[str] | None:
        if node in stack:
            return path[path.index(node):]

        if node in visited:
            return None

        visited.add(node)
        stack.add(node)

        for neighbour in graph.get(node, []):
            cycle: List[str] | None = dfs(neighbour, path + [node])
            if cycle:
                return cycle

        stack.remove(node)
        return None

    for node in graph:
        cycle: List[str] | None = dfs(node, [])
        if cycle:
            return cycle

    return None


def remove_cycle(graph: Dict[str, List[str]], cycle: List[str]) -> Dict[str, List[str]]:
    # Удаляем первое ребро в цикле
    from_node: str = cycle[0]
    to_node: str = cycle[1]
    graph[from_node].remove(to_node)
    print(f"Removed edge: {from_node} -> {to_node}")
    return graph


def topological_sort(graph: DefaultDict[str, List[str]]) -> List[str]:
    graph: DefaultDict[str, List[str]] = {
        node: list(set(deps))
        for node, deps in graph.items()
    }
    # Подсчёт входящих рёбер для каждой вершины
    in_degree: DefaultDict[str, int] = defaultdict(int)
    for node, dependencies in graph.items():
        for dependency in dependencies:
            in_degree[dependency] += 1

    # Очередь для вершин с 0 входящими рёбрами
    zero_in_degree = deque(node for node in graph if in_degree[node] == 0)
    sorted_order: List[str] = []

    while zero_in_degree:
        current = zero_in_degree.popleft()
        sorted_order.append(current)

        # Уменьшаем степень входа для соседей
        for neighbor in graph.get(current, []):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                zero_in_degree.append(neighbor)

    # Проверка на наличие цикла
    if len(sorted_order) != len(graph):
        while True:#find_cycle(graph):
            cycle: List[str] | None = find_cycle(graph)
            if cycle:
                graph: DefaultDict[str, list[str]] = remove_cycle(graph, cycle)
                continue
            break

        return topological_sort(graph)
        
        # raise ValueError("Graph contains a cycle. Topological sort is not possible.")

    return sorted_order
