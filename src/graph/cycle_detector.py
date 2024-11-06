from typing import List, Tuple
from sqlalchemy import text
from src.db.database import SessionLocal


class CycleDetector:
    """Class to handle cycle detection in graphs."""

    @staticmethod
    def find_cycles(graph_id: str) -> List[List[str]]:
        """
        Find all unique cycles in a graph.

        Args:
            graph_id: The ID of the graph to analyze

        Returns:
            List of cycles, where each cycle is a list of node IDs.
            Each cycle is normalized to start with the lexicographically smallest node ID.
        """
        with SessionLocal() as session:
            result = session.execute(
                text("SELECT * FROM find_cycles(:graph_id)"),
                {"graph_id": graph_id}
            )

            cycles = []
            seen = set()  # To ensure uniqueness
            for row in result:
                cycle_tuple = tuple(row.cycle_node_ids)
                if cycle_tuple not in seen:
                    cycles.append(list(cycle_tuple))
                    seen.add(cycle_tuple)

            return cycles

    @staticmethod
    def detect_has_cycle(graph_id: str) -> bool:
        """
        Check if a graph contains any cycles.

        Args:
            graph_id: The ID of the graph to check

        Returns:
            True if the graph contains at least one cycle, False otherwise
        """
        cycles = CycleDetector.find_cycles(graph_id)
        return len(cycles) > 0