import pytest
from src.xml_processor.parser import GraphXMLParser
from src.utils.exceptions import XMLValidationError


@pytest.fixture
def parser():
    return GraphXMLParser()


@pytest.fixture
def valid_graph_xml(tmp_path):
    content = """<?xml version="1.0" encoding="UTF-8"?>
<graph>
    <id>g1_test</id>
    <name>Valid Test Graph</name>
    <nodes>
        <node>
            <id>a</id>
            <name>Node A</name>
        </node>
        <node>
            <id>b</id>
            <name>Node B</name>
        </node>
        <node>
            <id>c</id>
            <name>Node C</name>
        </node>
    </nodes>
    <edges>
        <node>
            <id>e1</id>
            <from>a</from>
            <to>b</to>
            <cost>42</cost>
        </node>
        <node>
            <id>e2</id>
            <from>b</from>
            <to>c</to>
        </node>
        <node>
            <id>e3</id>
            <from>a</from>
            <to>c</to>
            <cost>10.5</cost>
        </node>
    </edges>
</graph>"""
    xml_file = tmp_path / "valid_graph.xml"
    xml_file.write_text(content)
    return str(xml_file)


@pytest.fixture
def duplicate_nodes_xml(tmp_path):
    content = """<?xml version="1.0" encoding="UTF-8"?>
<graph>
    <id>g2_test</id>
    <name>Graph with Duplicate Nodes</name>
    <nodes>
        <node>
            <id>a</id>
            <name>Node A</name>
        </node>
        <node>
            <id>a</id>
            <name>Node A Duplicate</name>
        </node>
    </nodes>
    <edges>
        <node>
            <id>e1</id>
            <from>a</from>
            <to>a</to>
            <cost>1</cost>
        </node>
    </edges>
</graph>"""
    xml_file = tmp_path / "duplicate_nodes.xml"
    xml_file.write_text(content)
    return str(xml_file)


@pytest.fixture
def missing_name_xml(tmp_path):
    content = """<?xml version="1.0" encoding="UTF-8"?>
<graph>
    <id>g3_test</id>
    <nodes>
        <node>
            <id>a</id>
            <name>Node A</name>
        </node>
    </nodes>
    <edges>
    </edges>
</graph>"""
    xml_file = tmp_path / "missing_name.xml"
    xml_file.write_text(content)
    return str(xml_file)


@pytest.fixture
def negative_cost_xml(tmp_path):
    content = """<?xml version="1.0" encoding="UTF-8"?>
<graph>
    <id>g4_test</id>
    <name>Graph with Negative Cost</name>
    <nodes>
        <node>
            <id>a</id>
            <name>Node A</name>
        </node>
        <node>
            <id>b</id>
            <name>Node B</name>
        </node>
    </nodes>
    <edges>
        <node>
            <id>e1</id>
            <from>a</from>
            <to>b</to>
            <cost>-10</cost>
        </node>
    </edges>
</graph>"""
    xml_file = tmp_path / "negative_cost.xml"
    xml_file.write_text(content)
    return str(xml_file)


@pytest.fixture
def nonexistent_node_xml(tmp_path):
    content = """<?xml version="1.0" encoding="UTF-8"?>
<graph>
    <id>g5_test</id>
    <name>Graph with Invalid Edge Reference</name>
    <nodes>
        <node>
            <id>a</id>
            <name>Node A</name>
        </node>
    </nodes>
    <edges>
        <node>
            <id>e1</id>
            <from>a</from>
            <to>b</to>
            <cost>5</cost>
        </node>
    </edges>
</graph>"""
    xml_file = tmp_path / "nonexistent_node.xml"
    xml_file.write_text(content)
    return str(xml_file)


@pytest.fixture
def missing_node_id_xml(tmp_path):
    content = """<?xml version="1.0" encoding="UTF-8"?>
<graph>
    <id>g6_test</id>
    <name>Graph with Missing Node ID</name>
    <nodes>
        <node>
            <name>Node A</name>
        </node>
    </nodes>
    <edges>
    </edges>
</graph>"""
    xml_file = tmp_path / "missing_node_id.xml"
    xml_file.write_text(content)
    return str(xml_file)


@pytest.fixture
def invalid_cost_xml(tmp_path):
    content = """<?xml version="1.0" encoding="UTF-8"?>
<graph>
    <id>g7_test</id>
    <name>Graph with Invalid Cost</name>
    <nodes>
        <node>
            <id>a</id>
            <name>Node A</name>
        </node>
        <node>
            <id>b</id>
            <name>Node B</name>
        </node>
    </nodes>
    <edges>
        <node>
            <id>e1</id>
            <from>a</from>
            <to>b</to>
            <cost>not_a_number</cost>
        </node>
    </edges>
</graph>"""
    xml_file = tmp_path / "invalid_cost.xml"
    xml_file.write_text(content)
    return str(xml_file)


class TestXMLProcessor:
    def test_valid_graph(self, parser, valid_graph_xml):
        """Test parsing and validation of a valid graph"""
        graph_data = parser.parse_file(valid_graph_xml)

        assert graph_data['id'] == 'g1_test'
        assert graph_data['name'] == 'Valid Test Graph'
        assert len(graph_data['nodes']) == 3
        assert len(graph_data['edges']) == 3

        node_ids = {node['id'] for node in graph_data['nodes']}
        assert node_ids == {'a', 'b', 'c'}

        edge = graph_data['edges'][0]
        assert edge['from'] == 'a'
        assert edge['to'] == 'b'
        assert edge['cost'] == 42.0

    def test_duplicate_nodes(self, parser, duplicate_nodes_xml):
        """Test that duplicate node IDs are caught"""
        with pytest.raises(XMLValidationError, match="Duplicate node id found"):
            parser.parse_file(duplicate_nodes_xml)

    def test_missing_name(self, parser, missing_name_xml):
        """Test that missing graph name is caught"""
        with pytest.raises(XMLValidationError, match="Missing required element: name"):
            parser.parse_file(missing_name_xml)

    def test_negative_cost(self, parser, negative_cost_xml):
        """Test that negative edge costs are caught"""
        with pytest.raises(XMLValidationError, match="Edge cost must be non-negative: -10.0"):
            parser.parse_file(negative_cost_xml)

    def test_nonexistent_node(self, parser, nonexistent_node_xml):
        """Test that edges referencing non-existent nodes are caught"""
        with pytest.raises(XMLValidationError, match="Edge references non-existent.*node"):
            parser.parse_file(nonexistent_node_xml)

    def test_load_nonexistent_file(self, parser):
        """Test handling of non-existent files"""
        with pytest.raises(XMLValidationError):
            parser.parse_file("nonexistent_file.xml")

    def test_missing_node_id(self, parser, missing_node_id_xml):
        """Test that missing node ID is caught"""
        with pytest.raises(XMLValidationError, match="Missing required element: id"):
            parser.parse_file(missing_node_id_xml)

    def test_invalid_cost(self, parser, invalid_cost_xml):
        """Test that invalid cost value is caught"""
        with pytest.raises(XMLValidationError, match="Invalid cost value for edge"):
            parser.parse_file(invalid_cost_xml)
