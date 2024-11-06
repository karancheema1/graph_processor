-- Function to find all cycles in a graph
CREATE OR REPLACE FUNCTION find_cycles(graph_id_param TEXT)
RETURNS TABLE (
    cycle_path INTEGER[],
    cycle_node_ids TEXT[]
) AS $$
WITH RECURSIVE paths(last_node, path, path_nodes, is_cycle) AS (
    -- Start from each node in the graph
    SELECT
        e.to_node_id,
        ARRAY[e.from_node_id, e.to_node_id],
        ARRAY[n1.node_id, n2.node_id],
        false
    FROM edges e
    JOIN nodes n1 ON e.from_node_id = n1.id
    JOIN nodes n2 ON e.to_node_id = n2.id
    WHERE e.graph_id = graph_id_param

    UNION ALL

    -- Recursively follow edges
    SELECT
        e.to_node_id,
        p.path || e.to_node_id,
        p.path_nodes || n2.node_id,
        e.to_node_id = ANY(p.path)
    FROM paths p
    JOIN edges e ON e.from_node_id = p.last_node
    JOIN nodes n2 ON e.to_node_id = n2.id
    WHERE
        e.graph_id = graph_id_param
        AND NOT p.is_cycle
        AND array_length(p.path, 1) < (
            SELECT count(*) + 1 FROM nodes WHERE graph_id = graph_id_param
        )
),
-- Get all cycles
raw_cycles AS (
    SELECT DISTINCT
        cycle.path,
        cycle.path_nodes
    FROM paths cycle
    WHERE
        cycle.is_cycle
        AND cycle.path[1] = cycle.path[array_length(cycle.path, 1)]
        AND array_length(cycle.path, 1) > 2
),
-- Normalize cycles by rotating to start with the smallest node_id
normalized_cycles AS (
    SELECT
        path,
        path_nodes,
        (SELECT min(idx)
         FROM generate_subscripts(path_nodes, 1) idx
         WHERE idx < array_length(path_nodes, 1)
         AND path_nodes[idx] = (
             SELECT min(elem)
             FROM unnest(path_nodes[1:array_length(path_nodes, 1)-1]) elem
         )
        ) as min_idx
    FROM raw_cycles
)
-- Return normalized unique cycles
SELECT DISTINCT
    array_cat(
        path[min_idx:array_length(path, 1)-1],
        path[1:min_idx]
    ) as cycle_path,
    array_cat(
        path_nodes[min_idx:array_length(path_nodes, 1)-1],
        path_nodes[1:min_idx]
    ) as cycle_node_ids
FROM normalized_cycles;
$$ LANGUAGE SQL;