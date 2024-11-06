import sys
import json
from typing import Dict, List, Any
from sqlalchemy import select, inspect

from src.graph.path_finder import PathFinder
from src.xml_processor.parser import GraphXMLParser
from src.db.models import Graph, Node, Edge
from src.db.database import SessionLocal, engine


from src.db.database import ensure_db_initialized

def ensure_db_tables_exist():
    ensure_db_initialized()


def check_graph_exists(graph_id: str) -> bool:
    with SessionLocal() as session:
        stmt = select(Graph).where(Graph.id == graph_id)
        graph = session.execute(stmt).scalar()
        return graph is not None


def process_single_query(query: Dict, path_finder: PathFinder) -> Dict[str, Any]:
    if "paths" in query:
        paths_query = query["paths"]
        start = paths_query["start"]
        end = paths_query["end"]

        paths = path_finder.find_all_paths(start, end)
        return {
            "paths": {
                "from": start,
                "to": end,
                "paths": paths
            }
        }

    elif "cheapest" in query:
        cheapest_query = query["cheapest"]
        start = cheapest_query["start"]
        end = cheapest_query["end"]

        path = path_finder.find_cheapest_path(start, end)
        return {
            "cheapest": {
                "from": start,
                "to": end,
                "path": path if path is not None else False
            }
        }

    return {}


def process_queries(input_data: Dict) -> Dict[str, List[Dict[str, Any]]]:
    graph_id = input_data.get("graph_id")
    if not graph_id:
        raise ValueError("graph_id is required in the input JSON")

    ensure_db_tables_exist()

    if not check_graph_exists(graph_id):
        return {
            "error": f"Graph with ID '{graph_id}' does not exist in the database"
        }

    path_finder = PathFinder(graph_id)

    answers = []
    for query in input_data.get("queries", []):
        result = process_single_query(query, path_finder)
        if result:
            answers.append(result)

    return {"answers": answers}


def parse_xml(file_path: str, save_to_db: bool = False) -> None:
    """Parse XML file and optionally save to database."""
    parser = GraphXMLParser()
    try:
        result = parser.parse_file(file_path)
        print('\nParsing successful! Graph structure:')
        print(f'Graph ID: {result["id"]}')
        print(f'Graph Name: {result["name"]}')
        print(f'Number of nodes: {len(result["nodes"])}')
        print(f'Number of edges: {len(result["edges"])}')

        if save_to_db:
            ensure_db_tables_exist()

            session = SessionLocal()
            try:
                # Create graph
                graph = Graph(id=result['id'], name=result['name'])
                session.add(graph)
                session.flush()

                # Create nodes
                node_map = {}
                for node_data in result['nodes']:
                    node = Node(
                        node_id=node_data['id'],
                        name=node_data['name'],
                        graph_id=graph.id
                    )
                    session.add(node)
                    node_map[node_data['id']] = node
                session.flush()

                # Create edges
                for edge_data in result['edges']:
                    edge = Edge(
                        edge_id=edge_data['id'],
                        from_node_id=node_map[edge_data['from']].id,
                        to_node_id=node_map[edge_data['to']].id,
                        cost=edge_data.get('cost', 0.0),
                        graph_id=graph.id
                    )
                    session.add(edge)

                session.commit()
                print('\nSuccessfully saved to database!')

            except Exception as e:
                print(f'\nDatabase Error: {str(e)}')
                session.rollback()
                sys.exit(1)
            finally:
                session.close()

    except Exception as e:
        print(f'\nError: {str(e)}')
        sys.exit(1)


def print_usage():
    print("""
Usage:
    Parse XML only:     python -m src.main parse <xml_file>
    Parse & save XML:   python -m src.main save <xml_file>
    Process queries:    python -m src.main query < input.json
    """)


def main():
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    command = sys.argv[1]

    if command in ['parse', 'save']:
        if len(sys.argv) != 3:
            print_usage()
            sys.exit(1)
        xml_file = sys.argv[2]
        parse_xml(xml_file, save_to_db=(command == 'save'))

    elif command == 'query':
        try:
            # Read input JSON from stdin
            input_data = json.load(sys.stdin)
            # Process queries and get results
            results = process_queries(input_data)
            # Write results to stdout
            json.dump(results, sys.stdout, indent=2)
            sys.stdout.write('\n')
        except json.JSONDecodeError as e:
            sys.stderr.write(f"Error: Invalid JSON input - {str(e)}\n")
            sys.exit(1)
        except ValueError as e:
            sys.stderr.write(f"Error: {str(e)}\n")
            sys.exit(1)
        except Exception as e:
            sys.stderr.write(f"Error: {str(e)}\n")
            sys.exit(1)

    else:
        print_usage()
        sys.exit(1)


if __name__ == "__main__":
    main()