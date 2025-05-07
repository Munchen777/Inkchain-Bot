import openpyxl
import os
import sys
import networkx as nx

from collections import Counter, defaultdict, deque
from better_proxy import Proxy
from openpyxl.utils.exceptions import InvalidFileException
from typing import DefaultDict, Dict, Deque, List, Set

from generall_settings import EXCEL_FILE_PATH
from modules import Logger
from modules.interfaces import BaseModuleInfo


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

def find_least_significant_edge(cycle_edges: List[str], graph: DefaultDict[str, List[str]]):
    """ Определяет, какое ребро удалить """
    # Считаем входящие связи
    in_degree = Counter()
    for u in graph:
        for v in graph.get(u, []):
            in_degree[v] += 1

    # Выбираем ребро, ведущее в вершину с минимальной входящей степенью
    min_edge = min(cycle_edges, key=lambda edge: in_degree[edge[1]])
    return min_edge


def find_cycle(graph: DefaultDict[str, List[str]]) -> List[str] | None:
    """ Находит любое ребро в цикле """
    visited: Dict[str, bool] = {node: False for node in graph}
    rec_stack: Dict[str, bool] = {node: False for node in graph}

    def dfs_cycle_detect(node: str, visited: Dict[str, bool], rec_stack: Dict[str, bool]):
        """ Обнаружение цикла с помощью DFS """
        visited[node] = True
        rec_stack[node] = True

        for neighbour in graph.get(node, []):
            if not visited.get(neighbour):
                cycle_edge = dfs_cycle_detect(neighbour, visited, rec_stack)
                if cycle_edge:
                    return cycle_edge

            elif rec_stack.get(neighbour):  # Цикл найден
                return (node, neighbour)

        rec_stack[node] = False
        return None

    for node in graph:
        if not visited.get(node):
            cycle_edge = dfs_cycle_detect(node, visited, rec_stack)
            if cycle_edge:
                return cycle_edge
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
    cycle_edges: List = []

    while True:
        cycle_edge = find_cycle(graph)
        if not cycle_edge:
            break

        cycle_edges.append(cycle_edge)
        edge_to_remove = find_least_significant_edge(cycle_edges, graph)
        print(f"Удаляем ребро {edge_to_remove}")
        graph[edge_to_remove[0]].remove(edge_to_remove[1])
        cycle_edges.remove(edge_to_remove)


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
        problematic_nodes = [node for node in graph if in_degree[node] > 0]
        for u in graph:
            for v in graph.get(u, []):
                if v in problematic_nodes:
                    print(f"Удаляем ребро ({u} -> {v})")
                    graph[u].remove(v)
        # while True:#find_cycle(graph):
        #     cycle: List[str] | None = find_cycle(graph)
        #     if cycle:
        #         graph: DefaultDict[str, list[str]] = remove_cycle(graph, cycle)
        #         continue
        #     break

        # return topological_sort(graph)
        
        # raise ValueError("Graph contains a cycle. Topological sort is not possible.")

    return sorted_order


async def build_route_modules(
    modules_to_execute: Dict[str, BaseModuleInfo],
    all_available_wallet_balances: Dict[str, Dict[str, float]]
):
    graph: nx.Graph = nx.Graph()
    
    for module_name, module in modules_to_execute.items():
        graph.add_node(module_name,
                       source_tokens=module.source_token, 
                       dest_tokens=module.dest_token,
                       source_network=module.source_network,
                       dest_network=module.destination_network,
                       )
    """
    1. Сверяем сети отправления текущего модуля с сетью назначения
    2. Можем ли мы получить токен отправления в токенах назначения, иначе False
    3. Проверяю, что токенов в сети 
    
    
    """
    for node1 in graph.nodes:
        for node2 in graph.nodes:
            if node1 != node2:
                # Берем два модуля
                module_1: BaseModuleInfo = modules_to_execute.get(node1)
                module_2: BaseModuleInfo = modules_to_execute.get(node2)

                source_tokens: List[str] | None = module_1.source_token if isinstance(module_1.source_token, list) else [module_1.source_token]
                source_network: str | None = module_1.source_network
                
                dest_tokens: List[str] | None = module_2.dest_token if isinstance(module_2.dest_token, list) else [module_2.dest_token]
                dest_network: str | None = module_2.destination_network
                
                # Если сеть отправления 1-го модуля равна сети назначения и
                # не хватает баланса какого-нибудь токена в сети отправления на выполнение действия 
                # (оставляем в сети отправления мин.баланс + сумма для действия)
                if source_network == dest_network and any(
                    all_available_wallet_balances.get(source_network, {}).get(token_name, 0) <= (module_1.min_available_balance + module_1.min_amount_out) \
                        for token_name in source_tokens
                    ) and all(token in dest_tokens for token in source_tokens):
                    # Если в сети назначения хватает баланса для сети отправления (мин. баланс + мин.сумма на выходе)
                    
                    # Если в сети отправления другого модуля хватает баланса токенов, то создаем связь
                    dep_source_network: str = module_2.source_network
                    dep_source_tokens: List[str] | None = module_2.source_token if isinstance(module_2.source_token, list) else [module_2.source_token]
                    
                    if all(
                        all_available_wallet_balances.get(dep_source_network, {}).get(token_name, 0) > (module_2.min_available_balance + module_2.min_amount_out)
                        for token_name in dep_source_tokens
                    ) and module_1.module_type != module_2.module_type:
                        graph.add_edge(node2, node1)
                        
                        for token_name in dep_source_tokens:
                            all_available_wallet_balances.get(dep_source_network)[token_name] -= module_2.min_amount_out
                        
                        for token_name in source_tokens:
                            all_available_wallet_balances.get(source_network)[token_name] += module_2.min_amount_out
                
    
    return graph
    print()
                # if all_available_wallet_balances.get(source_network, {}).get(token_name, 0) > (module_1.min_available_balance + module_1.min_amount_out) \
                #     for token_name in source_tokens
                    
                
                
                    
                    
                    # if all(
                    #     all_available_wallet_balances.get(dest_network, {}).get(token_name, 0) > (module_1.min_available_balance)
                    #     for token_name in dest_tokens
                    # ):
                    #     graph.add_edge(node2, node1)
                    
                
                        

    
    
