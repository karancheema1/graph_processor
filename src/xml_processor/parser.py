from typing import Dict, Optional, Set
from lxml import etree
from src.utils.exceptions import XMLValidationError


class GraphXMLParser:

    def find_element(self, element: etree.Element, child: str) -> Optional[etree.Element]:
        found = element.find(child)
        if found is None:
            raise XMLValidationError(f"Missing required element: {child}")
        return found

    def find_text(self, element: etree.Element, text: str) -> str:
        found = self.find_element(element, text)
        if found.text is None:
            raise XMLValidationError(f"Missing text for element: {text}")
        return found.text

    def _validate_nodes(self, nodes: list) -> None:
        node_ids = set()
        for node in nodes:
            if node['id'] in node_ids:
                raise XMLValidationError(f"Duplicate node id found: {node['id']}")
            node_ids.add(node['id'])

        if not nodes:
            raise XMLValidationError("Graph must have at least one node")

    def _validate_edges(self, edges: list, valid_node_ids: Set[str]) -> None:
        for edge in edges:
            if edge['from'] not in valid_node_ids:
                raise XMLValidationError(f"Edge references non-existent from node: {edge['from']}")
            if edge['to'] not in valid_node_ids:
                raise XMLValidationError(f"Edge references non-existent to node: {edge['to']}")

            if edge['cost'] < 0:
                raise XMLValidationError(f"Edge cost must be non-negative: {edge['cost']}")

    def parse_file(self, file_path: str) -> Dict:
        try:
            tree = etree.parse(file_path)
            root = tree.getroot()

            # Create graph data to be displayed in stdout
            graph_data = {
                'id': self.find_text(root, 'id'),
                'name': self.find_text(root, 'name'),
                'nodes': [],
                'edges': []
            }

            nodes_element = self.find_element(root, 'nodes')
            for node in nodes_element.findall('node'):
                node_data = {
                    'id': self.find_text(node, 'id'),
                    'name': self.find_text(node, 'name')
                }
                graph_data['nodes'].append(node_data)

            self._validate_nodes(graph_data['nodes'])
            valid_node_ids = {node['id'] for node in graph_data['nodes']}

            edges_element = root.find('edges')
            if edges_element is not None:
                for edge in edges_element.findall('node'):
                    edge_data = {
                        'id': self.find_text(edge, 'id'),
                        'from': self.find_text(edge, 'from'),
                        'to': self.find_text(edge, 'to')
                    }

                    cost_elem = edge.find('cost')
                    try:
                        edge_data['cost'] = float(cost_elem.text) if cost_elem is not None else 0.0
                    except (ValueError, AttributeError):
                        raise XMLValidationError(
                            f"Invalid cost value for edge {edge_data['id']}"
                        )

                    graph_data['edges'].append(edge_data)

                self._validate_edges(graph_data['edges'], valid_node_ids)

            return graph_data

        except etree.DocumentInvalid as e:
            raise XMLValidationError(f"XML validation failed: {str(e)}")
        except etree.XMLSyntaxError as e:
            raise XMLValidationError(f"XML syntax error: {str(e)}")
        except XMLValidationError:
            raise
        except Exception as e:
            raise XMLValidationError(f"Failed to parse XML: {str(e)}")