from src.graph.path_finder import PathFinder
from src.db.models import Graph, Node, Edge


def create_test_graph(session) -> Graph:
    """Create a test graph with known paths."""
    graph = Graph(id="test_graph", name="Test Graph")
    session.add(graph)
    session.flush()

    nodes = {}
    for node_id in ['a', 'b', 'c', 'd', 'e']:
        node = Node(
            node_id=node_id,
            name=f"Node {node_id.upper()}",
            graph_id=graph.id
        )
        session.add(node)
        session.flush()
        nodes[node_id] = node

    edges_data = [
        ('e1', 'a', 'b', 1),
        ('e2', 'b', 'e', 2),
        ('e3', 'a', 'c', 2),
        ('e4', 'c', 'd', 1),
        ('e5', 'd', 'e', 3),
    ]

    for edge_id, from_id, to_id, cost in edges_data:
        edge = Edge(
            edge_id=edge_id,
            from_node_id=nodes[from_id].id,
            to_node_id=nodes[to_id].id,
            cost=cost,
            graph_id=graph.id
        )
        session.add(edge)

    session.commit()
    return graph


class TestPathFinder:
    def test_find_all_paths(self, test_db):
        graph = create_test_graph(test_db)
        finder = PathFinder(graph.id)

        paths = finder.find_all_paths('a', 'e')
        assert len(paths) == 2
        assert ['a', 'b', 'e'] in paths
        assert ['a', 'c', 'd', 'e'] in paths

    def test_find_cheapest_path(self, test_db):
        graph = create_test_graph(test_db)
        finder = PathFinder(graph.id)

        path = finder.find_cheapest_path('a', 'e')
        assert path == ['a', 'b', 'e']

    def test_nonexistent_path(self, test_db):
        graph = create_test_graph(test_db)
        finder = PathFinder(graph.id)

        paths = finder.find_all_paths('a', 'x')
        assert paths == []

        path = finder.find_cheapest_path('a', 'x')
        assert path is False

    def test_same_node_path(self, test_db):
        graph = create_test_graph(test_db)
        finder = PathFinder(graph.id)

        paths = finder.find_all_paths('a', 'a')
        assert paths == []

        path = finder.find_cheapest_path('a', 'a')
        assert path is False