import pytest
from sqlalchemy.orm import Session
from src.db.models import Graph, Node, Edge
from src.graph.cycle_detector import CycleDetector


def create_test_graph(session: Session, graph_id: str) -> Graph:
    """Helper function to create a graph with given ID"""
    graph = Graph(id=graph_id, name=f"Test Graph {graph_id}")
    session.add(graph)
    session.commit()
    return graph


def create_test_node(session: Session, graph: Graph, node_id: str, name: str) -> Node:
    """Helper function to create a node"""
    node = Node(node_id=node_id, name=name, graph_id=graph.id)
    session.add(node)
    session.commit()
    return node


def create_test_edge(session: Session, graph: Graph, edge_id: str,
                     from_node: Node, to_node: Node, cost: float = 1.0) -> Edge:
    """Helper function to create an edge"""
    edge = Edge(
        edge_id=edge_id,
        from_node_id=from_node.id,
        to_node_id=to_node.id,
        cost=cost,
        graph_id=graph.id
    )
    session.add(edge)
    session.commit()
    return edge


class TestCycleDetection:
    def test_no_cycles(self, test_db):
        """Test a graph with no cycles"""
        graph = create_test_graph(test_db, "g1")
        node_a = create_test_node(test_db, graph, "a", "Node A")
        node_b = create_test_node(test_db, graph, "b", "Node B")
        node_c = create_test_node(test_db, graph, "c", "Node C")

        create_test_edge(test_db, graph, "e1", node_a, node_b)
        create_test_edge(test_db, graph, "e2", node_b, node_c)

        cycles = CycleDetector.find_cycles(graph.id)
        assert len(cycles) == 0
        assert not CycleDetector.detect_has_cycle(graph.id)

    def test_simple_cycle(self, test_db):
        """Test a graph with a simple cycle: A -> B -> C -> A"""
        graph = create_test_graph(test_db, "g2")
        node_a = create_test_node(test_db, graph, "a", "Node A")
        node_b = create_test_node(test_db, graph, "b", "Node B")
        node_c = create_test_node(test_db, graph, "c", "Node C")

        create_test_edge(test_db, graph, "e1", node_a, node_b)
        create_test_edge(test_db, graph, "e2", node_b, node_c)
        create_test_edge(test_db, graph, "e3", node_c, node_a)

        cycles = CycleDetector.find_cycles(graph.id)
        assert len(cycles) == 1
        assert cycles[0] == ["a", "b", "c", "a"]
        assert CycleDetector.detect_has_cycle(graph.id)

    def test_self_loop(self, test_db):
        """Test a graph with a self-loop: A -> A"""
        graph = create_test_graph(test_db, "g3")
        node_a = create_test_node(test_db, graph, "a", "Node A")

        create_test_edge(test_db, graph, "e1", node_a, node_a)

        cycles = CycleDetector.find_cycles(graph.id)
        assert len(cycles) == 0

    def test_multiple_cycles(self, test_db):
        """Test a graph with multiple cycles"""
        graph = create_test_graph(test_db, "g4")
        node_a = create_test_node(test_db, graph, "a", "Node A")
        node_b = create_test_node(test_db, graph, "b", "Node B")
        node_c = create_test_node(test_db, graph, "c", "Node C")
        node_d = create_test_node(test_db, graph, "d", "Node D")

        # Create cycle 1: A -> B -> C -> A
        create_test_edge(test_db, graph, "e1", node_a, node_b)
        create_test_edge(test_db, graph, "e2", node_b, node_c)
        create_test_edge(test_db, graph, "e3", node_c, node_a)

        # Create cycle 2: B -> C -> D -> B
        create_test_edge(test_db, graph, "e4", node_c, node_d)
        create_test_edge(test_db, graph, "e5", node_d, node_b)

        cycles = CycleDetector.find_cycles(graph.id)
        assert len(cycles) == 2
        assert ["a", "b", "c", "a"] in cycles
        assert ["b", "c", "d", "b"] in cycles
        assert CycleDetector.detect_has_cycle(graph.id)

    def test_complex_graph(self, test_db):
        """Test a complex graph with multiple paths and cycles"""
        graph = create_test_graph(test_db, "g5")

        nodes = {
            c: create_test_node(test_db, graph, c, f"Node {c.upper()}")
            for c in "abcdef"
        }

        edges = [
            ("a", "b"), ("b", "c"), ("c", "d"),
            ("d", "e"), ("e", "f"), ("f", "a"),
            ("b", "e"), ("c", "f"),
            ("d", "b")
        ]

        for i, (from_id, to_id) in enumerate(edges):
            create_test_edge(
                test_db, graph, f"e{i + 1}",
                nodes[from_id], nodes[to_id]
            )

        cycles = CycleDetector.find_cycles(graph.id)

        assert len(cycles) == 4
        assert ["a", "b", "c", "d", "e", "f", "a"] in cycles
        assert ['a', 'b', 'c', 'f', 'a'] in cycles
        assert ['a', 'b', 'e', 'f', 'a'] in cycles
        assert ["b", "c", "d", "b"] in cycles
        assert CycleDetector.detect_has_cycle(graph.id)

    def test_empty_graph(self, test_db):
        """Test a graph with no edges"""
        graph = create_test_graph(test_db, "g6")
        create_test_node(test_db, graph, "a", "Node A")
        create_test_node(test_db, graph, "b", "Node B")

        cycles = CycleDetector.find_cycles(graph.id)
        assert len(cycles) == 0
        assert not CycleDetector.detect_has_cycle(graph.id)

    def test_disconnected_cycles(self, test_db):
        """Test a graph with disconnected components containing cycles"""
        graph = create_test_graph(test_db, "g7")

        # First component: A -> B -> C -> A
        node_a1 = create_test_node(test_db, graph, "a1", "Node A1")
        node_b1 = create_test_node(test_db, graph, "b1", "Node B1")
        node_c1 = create_test_node(test_db, graph, "c1", "Node C1")

        create_test_edge(test_db, graph, "e1", node_a1, node_b1)
        create_test_edge(test_db, graph, "e2", node_b1, node_c1)
        create_test_edge(test_db, graph, "e3", node_c1, node_a1)

        # Second component: D -> E -> F -> D
        node_d = create_test_node(test_db, graph, "d", "Node D")
        node_e = create_test_node(test_db, graph, "e", "Node E")
        node_f = create_test_node(test_db, graph, "f", "Node F")

        create_test_edge(test_db, graph, "e4", node_d, node_e)
        create_test_edge(test_db, graph, "e5", node_e, node_f)
        create_test_edge(test_db, graph, "e6", node_f, node_d)

        cycles = CycleDetector.find_cycles(graph.id)
        assert len(cycles) == 2
        assert ["a1", "b1", "c1", "a1"] in cycles
        assert ["d", "e", "f", "d"] in cycles
        assert CycleDetector.detect_has_cycle(graph.id)
