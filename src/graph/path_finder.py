from typing import List, Optional, Dict, Any, Union
from collections import defaultdict
import heapq
from sqlalchemy import select
from src.db.database import SessionLocal
from src.db.models import Node, Edge


class PathFinder:
    def __init__(self, graph_id: str):
        self.graph_id = graph_id
        self.adjacency_list: Dict[str, List[tuple[str, float]]] = {}
        self._load_graph()

    def _load_graph(self) -> None:
        """Load graph structure from database into memory for efficient path finding"""
        with SessionLocal() as session:
            # Get all nodes and edges for this graph
            nodes = session.execute(
                select(Node).where(Node.graph_id == self.graph_id)
            ).scalars().all()

            edges = session.execute(
                select(Edge).where(Edge.graph_id == self.graph_id)
            ).scalars().all()

            # Initialize adjacency list with all nodes (even those without edges)
            self.adjacency_list = defaultdict(list)
            for node in nodes:
                self.adjacency_list[node.node_id]

            for edge in edges:
                # Get the from and to nodes
                from_node = session.get(Node, edge.from_node_id)
                to_node = session.get(Node, edge.to_node_id)
                if from_node and to_node:
                    self.adjacency_list[from_node.node_id].append(
                        (to_node.node_id, edge.cost)
                    )

    def find_all_paths(self, start: str, end: str) -> List[List[str]]:
        """
        Find all possible paths from start to end node, ignoring cycles.
        """
        if start not in self.adjacency_list or end not in self.adjacency_list:
            return []

        def dfs(current: str, target: str, path: List[str], paths: List[List[str]], visited: set) -> None:
            if current == target and len(path) > 1:  # Only add path if we've traversed edges
                paths.append(path[:])
                return

            visited.add(current)

            # Explore all neighbor nodes
            for next_node, _ in self.adjacency_list[current]:
                if next_node not in visited:
                    path.append(next_node)
                    dfs(next_node, target, path, paths, visited)
                    path.pop()

            visited.remove(current)

        all_paths: List[List[str]] = []
        visited: set = set()
        dfs(start, end, [start], all_paths, visited)
        return all_paths

    def find_cheapest_path(self, start: str, end: str) -> Union[List[str], bool]:
        """
        Find the cheapest path from start to end node using Dijkstra's algorithm.
        Returns False if no path exists or path to self is requested.
        """
        if start not in self.adjacency_list or end not in self.adjacency_list:
            return False

        # Special case: if start and end are the same, no path exists
        if start == end:
            return False

        # Initialize distances and predecessors
        distances = {node: float('infinity') for node in self.adjacency_list}
        distances[start] = 0
        predecessors = {node: None for node in self.adjacency_list}

        # Priority queue
        pq = [(0, start)]

        while pq:
            current_distance, current = heapq.heappop(pq)

            if current == end:
                # Found a path, reconstruct it
                path = []
                while current is not None:
                    path.append(current)
                    current = predecessors[current]
                return path[::-1]

            if current_distance > distances[current]:
                continue

            for neighbor, cost in self.adjacency_list[current]:
                distance = current_distance + cost

                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    predecessors[neighbor] = current
                    heapq.heappush(pq, (distance, neighbor))

        return False  # No path found