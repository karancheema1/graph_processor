CREATE TABLE graphs (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_graph_id CHECK (length(id) > 0)
);
COMMENT ON TABLE graphs IS 'Stores metadata about each graph';
COMMENT ON COLUMN graphs.id IS 'Unique identifier for the graph, from XML id element';
COMMENT ON COLUMN graphs.name IS 'Human-readable name of the graph, from XML name element';

CREATE TABLE nodes (
    id SERIAL PRIMARY KEY,
    node_id TEXT NOT NULL,
    name TEXT NOT NULL,
    graph_id TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_graph FOREIGN KEY (graph_id) REFERENCES graphs(id) ON DELETE CASCADE,
    CONSTRAINT unique_node_per_graph UNIQUE (node_id, graph_id),
    CONSTRAINT valid_node_id CHECK (length(node_id) > 0)
);
COMMENT ON TABLE nodes IS 'Stores vertices (nodes) of each graph';
COMMENT ON COLUMN nodes.id IS 'Internal unique identifier for the node';
COMMENT ON COLUMN nodes.node_id IS 'Node identifier from XML, unique within a graph';
COMMENT ON COLUMN nodes.name IS 'Human-readable name of the node';
COMMENT ON COLUMN nodes.graph_id IS 'Reference to the graph this node belongs to';

CREATE TABLE edges (
    id SERIAL PRIMARY KEY,
    edge_id TEXT NOT NULL,
    from_node_id INTEGER NOT NULL,
    to_node_id INTEGER NOT NULL,
    cost DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    graph_id TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_from_node FOREIGN KEY (from_node_id) REFERENCES nodes(id) ON DELETE CASCADE,
    CONSTRAINT fk_to_node FOREIGN KEY (to_node_id) REFERENCES nodes(id) ON DELETE CASCADE,
    CONSTRAINT fk_graph FOREIGN KEY (graph_id) REFERENCES graphs(id) ON DELETE CASCADE,
    CONSTRAINT unique_edge_per_graph UNIQUE (edge_id, graph_id),
    CONSTRAINT valid_edge_id CHECK (length(edge_id) > 0),
    CONSTRAINT positive_cost CHECK (cost >= 0)
);
COMMENT ON TABLE edges IS 'Stores directed edges connecting nodes in each graph';
COMMENT ON COLUMN edges.id IS 'Internal unique identifier for the edge';
COMMENT ON COLUMN edges.edge_id IS 'Edge identifier from XML, unique within a graph';
COMMENT ON COLUMN edges.from_node_id IS 'Reference to the source node';
COMMENT ON COLUMN edges.to_node_id IS 'Reference to the target node';
COMMENT ON COLUMN edges.cost IS 'Non-negative weight/cost of traversing this edge';
COMMENT ON COLUMN edges.graph_id IS 'Reference to the graph this edge belongs to';

-- Indexes for performance
CREATE INDEX idx_nodes_graph_id ON nodes(graph_id);
CREATE INDEX idx_edges_graph_id ON edges(graph_id);
CREATE INDEX idx_edges_nodes ON edges(from_node_id, to_node_id);