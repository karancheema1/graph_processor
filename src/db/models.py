from src.db.database import Base
from sqlalchemy import Column, Integer, String, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

class Graph(Base):
    """
    Represents a directed graph.

    Attributes:
        id (str): Primary key for the graph
        name (str): Name of the graph
        nodes (relationship): One-to-many relationship with Node table
        edges (relationship): One-to-many relationship with Edge table
    """
    __tablename__ = 'graphs'

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)

    nodes = relationship("Node", back_populates="graph", cascade="all, delete-orphan")
    edges = relationship("Edge", back_populates="graph", cascade="all, delete-orphan")


class Node(Base):
    """
    Represents a node in a graph.

    Attributes:
        id (int): Auto-incrementing primary key
        node_id (str): User-provided node identifier
        name (str): Name of the node
        graph_id (str): Foreign key reference to the parent graph
    """
    __tablename__ = 'nodes'

    id = Column(Integer, primary_key=True)
    node_id = Column(String, nullable=False)
    name = Column(String, nullable=False)
    graph_id = Column(String, ForeignKey('graphs.id', ondelete='CASCADE'), nullable=False)

    __table_args__ = (
        UniqueConstraint('graph_id', 'node_id', name='unique_graph_node'),
    )

    graph = relationship("Graph", back_populates="nodes")
    outgoing_edges = relationship("Edge", back_populates="from_node", foreign_keys="Edge.from_node_id")
    incoming_edges = relationship("Edge", back_populates="to_node", foreign_keys="Edge.to_node_id")


class Edge(Base):
    """
    Represents a directed edge in a graph.

    Attributes:
        id (int): Auto-incrementing primary key
        edge_id (str): User-provided edge identifier
        from_node_id (int): Foreign key reference to the source node
        to_node_id (int): Foreign key reference to the target node
        cost (float): Cost of the edge, defaults to 0.0
        graph_id (str): Foreign key reference to the parent graph
    """
    __tablename__ = 'edges'

    id = Column(Integer, primary_key=True)
    edge_id = Column(String, nullable=False)
    from_node_id = Column(Integer, ForeignKey('nodes.id', ondelete='CASCADE'), nullable=False)
    to_node_id = Column(Integer, ForeignKey('nodes.id', ondelete='CASCADE'), nullable=False)
    cost = Column(Float, nullable=False, default=0.0)
    graph_id = Column(String, ForeignKey('graphs.id', ondelete='CASCADE'), nullable=False)

    __table_args__ = (
        UniqueConstraint('graph_id', 'edge_id', name='unique_graph_edge'),
    )

    graph = relationship("Graph", back_populates="edges")
    from_node = relationship("Node", foreign_keys=[from_node_id], back_populates="outgoing_edges")
    to_node = relationship("Node", foreign_keys=[to_node_id], back_populates="incoming_edges")
