"""
Tests for the Flowchart & UX Ideation View module.
"""

import os
import unittest
from unittest.mock import patch, MagicMock

# Import the module to test
from ideater.modules.flowchart_view import (
    FlowchartView,
    DiagramType,
    DiagramNode,
    DiagramEdge,
    FlowchartRequest,
    FlowchartResult,
    SequenceDiagramRequest,
    SequenceDiagramResult,
    StateMachineDiagramRequest,
    StateMachineDiagramResult,
    ComponentDiagramRequest,
    ComponentDiagramResult,
)

class TestFlowchartView(unittest.TestCase):
    """Test cases for the FlowchartView class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a mock OpenAI client
        self.openai_patcher = patch('ideater.modules.flowchart_view.flowchart_view.openai')
        self.mock_openai = self.openai_patcher.start()
        
        # Create a mock config
        self.config_patcher = patch('ideater.modules.flowchart_view.flowchart_view.config')
        self.mock_config = self.config_patcher.start()
        
        # Configure the mock config
        self.mock_config.get_openai_api_key.return_value = "test_api_key"
        self.mock_config.get_openai_model.return_value = "gpt-4-turbo"
        self.mock_config.get_temperature.return_value = 0.7
        self.mock_config.get_max_tokens.return_value = 1500
        self.mock_config.get_mermaid_cli_path.return_value = "mmdc"
        self.mock_config.get_graphviz_path.return_value = "dot"
        
        # Create a mock OpenAI client
        self.mock_client = MagicMock()
        self.mock_openai.OpenAI.return_value = self.mock_client
        
        # Create a mock response for the OpenAI API
        self.mock_response = MagicMock()
        self.mock_response.choices = [MagicMock()]
        self.mock_response.choices[0].message.content = "flowchart TD\n    A[Start] --> B[Process]\n    B --> C[End]"
        self.mock_client.chat.completions.create.return_value = self.mock_response
        
        # Create a mock subprocess
        self.subprocess_patcher = patch('ideater.modules.flowchart_view.flowchart_view.subprocess')
        self.mock_subprocess = self.subprocess_patcher.start()
        
        # Create a mock tempfile
        self.tempfile_patcher = patch('ideater.modules.flowchart_view.flowchart_view.tempfile')
        self.mock_tempfile = self.tempfile_patcher.start()
        
        # Configure the mock tempfile
        self.mock_named_temp_file = MagicMock()
        self.mock_named_temp_file.__enter__.return_value.name = "test_file.mmd"
        self.mock_tempfile.NamedTemporaryFile.return_value = self.mock_named_temp_file
        
        # Create a mock open
        self.open_patcher = patch('builtins.open', unittest.mock.mock_open(read_data="<svg>test</svg>"))
        self.mock_open = self.open_patcher.start()
        
        # Create a mock os
        self.os_patcher = patch('ideater.modules.flowchart_view.flowchart_view.os')
        self.mock_os = self.os_patcher.start()
        
        # Create the FlowchartView instance
        self.flowchart_view = FlowchartView()
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.openai_patcher.stop()
        self.config_patcher.stop()
        self.subprocess_patcher.stop()
        self.tempfile_patcher.stop()
        self.open_patcher.stop()
        self.os_patcher.stop()
    
    def test_init(self):
        """Test initialization of FlowchartView."""
        self.assertEqual(self.flowchart_view.openai_api_key, "test_api_key")
        self.assertEqual(self.flowchart_view.openai_model, "gpt-4-turbo")
        self.assertEqual(self.flowchart_view.temperature, 0.7)
        self.assertEqual(self.flowchart_view.max_tokens, 1500)
        self.assertEqual(self.flowchart_view.mermaid_cli_path, "mmdc")
        self.assertEqual(self.flowchart_view.graphviz_path, "dot")
        self.assertEqual(self.flowchart_view.client, self.mock_client)
    
    def test_generate_flowchart(self):
        """Test generating a flowchart."""
        # Create a request
        request = FlowchartRequest(
            description="A simple flowchart",
            title="Test Flowchart",
            node_types=["process", "decision"],
            include_explanation=True
        )
        
        # Generate the flowchart
        result = self.flowchart_view.generate_flowchart(request)
        
        # Check the result
        self.assertIsInstance(result, FlowchartResult)
        self.assertEqual(result.mermaid_code, "flowchart TD\n    A[Start] --> B[Process]\n    B --> C[End]")
        self.assertEqual(len(result.nodes), 3)
        self.assertEqual(len(result.edges), 2)
        self.assertEqual(result.svg_data, "<svg>test</svg>")
        
        # Check that the OpenAI API was called correctly
        self.mock_client.chat.completions.create.assert_called_once()
        call_args = self.mock_client.chat.completions.create.call_args[1]
        self.assertEqual(call_args["model"], "gpt-4-turbo")
        self.assertEqual(call_args["temperature"], 0.7)
        self.assertEqual(call_args["max_tokens"], 1500)
        
        # Check that the messages include the description and title
        messages = call_args["messages"]
        self.assertEqual(len(messages), 2)
        self.assertIn("A simple flowchart", messages[1]["content"])
        self.assertIn("Test Flowchart", messages[1]["content"])
        
        # Check that the SVG was generated
        self.mock_subprocess.run.assert_called_once()
        self.mock_open.assert_called_once()
        self.mock_os.remove.assert_called()
    
    def test_generate_sequence_diagram(self):
        """Test generating a sequence diagram."""
        # Create a request
        request = SequenceDiagramRequest(
            description="A simple sequence diagram",
            title="Test Sequence Diagram",
            actors=["User", "System"],
            include_explanation=True
        )
        
        # Update the mock response for sequence diagrams
        self.mock_response.choices[0].message.content = "sequenceDiagram\n    participant User\n    participant System\n    User->>System: Request\n    System-->>User: Response"
        
        # Generate the sequence diagram
        result = self.flowchart_view.generate_sequence_diagram(request)
        
        # Check the result
        self.assertIsInstance(result, SequenceDiagramResult)
        self.assertEqual(result.mermaid_code, "sequenceDiagram\n    participant User\n    participant System\n    User->>System: Request\n    System-->>User: Response")
        self.assertEqual(len(result.actors), 2)
        self.assertEqual(len(result.messages), 2)
        self.assertEqual(result.svg_data, "<svg>test</svg>")
    
    def test_generate_state_machine_diagram(self):
        """Test generating a state machine diagram."""
        # Create a request
        request = StateMachineDiagramRequest(
            description="A simple state machine diagram",
            title="Test State Machine Diagram",
            initial_state="Idle",
            include_explanation=True
        )
        
        # Update the mock response for state machine diagrams
        self.mock_response.choices[0].message.content = "stateDiagram\n    [*] --> Idle\n    Idle --> Active: Start\n    Active --> Idle: Stop\n    Active --> [*]: End"
        
        # Generate the state machine diagram
        result = self.flowchart_view.generate_state_machine_diagram(request)
        
        # Check the result
        self.assertIsInstance(result, StateMachineDiagramResult)
        self.assertEqual(result.mermaid_code, "stateDiagram\n    [*] --> Idle\n    Idle --> Active: Start\n    Active --> Idle: Stop\n    Active --> [*]: End")
        self.assertEqual(len(result.states), 2)
        self.assertEqual(len(result.transitions), 4)
        self.assertEqual(result.svg_data, "<svg>test</svg>")
    
    def test_generate_component_diagram(self):
        """Test generating a component diagram."""
        # Create a request
        request = ComponentDiagramRequest(
            description="A simple component diagram",
            title="Test Component Diagram",
            components=["Frontend", "Backend", "Database"],
            include_explanation=True
        )
        
        # Update the mock response for component diagrams
        self.mock_response.choices[0].message.content = "classDiagram\n    class Frontend\n    class Backend\n    class Database\n    Frontend --> Backend\n    Backend --> Database"
        
        # Generate the component diagram
        result = self.flowchart_view.generate_component_diagram(request)
        
        # Check the result
        self.assertIsInstance(result, ComponentDiagramResult)
        self.assertEqual(result.mermaid_code, "classDiagram\n    class Frontend\n    class Backend\n    class Database\n    Frontend --> Backend\n    Backend --> Database")
        self.assertEqual(len(result.components), 3)
        self.assertEqual(len(result.relationships), 2)
        self.assertEqual(result.svg_data, "<svg>test</svg>")
    
    def test_update_diagram(self):
        """Test updating a diagram."""
        # Create a diagram
        mermaid_code = "flowchart TD\n    A[Start] --> B[Process]\n    B --> C[End]"
        
        # Update the mock response for updating diagrams
        self.mock_response.choices[0].message.content = "flowchart TD\n    A[Start] --> B[Process]\n    B --> D[New Step]\n    D --> C[End]"
        
        # Update the diagram
        updated_code = self.flowchart_view.update_diagram(
            diagram_type=DiagramType.FLOWCHART,
            mermaid_code=mermaid_code,
            instructions="Add a new step between Process and End"
        )
        
        # Check the result
        self.assertEqual(updated_code, "flowchart TD\n    A[Start] --> B[Process]\n    B --> D[New Step]\n    D --> C[End]")
        
        # Check that the OpenAI API was called correctly
        self.assertEqual(self.mock_client.chat.completions.create.call_count, 1)
    
    def test_parse_flowchart_mermaid(self):
        """Test parsing flowchart Mermaid code."""
        # Create a flowchart
        mermaid_code = "flowchart TD\n    A[Start] --> B[Process]\n    B --> C[End]"
        
        # Parse the flowchart
        nodes, edges = self.flowchart_view._parse_flowchart_mermaid(mermaid_code)
        
        # Check the result
        self.assertEqual(len(nodes), 3)
        self.assertEqual(len(edges), 2)
        
        # Check the nodes
        self.assertEqual(nodes[0].id, "A")
        self.assertEqual(nodes[0].label, "Start")
        self.assertEqual(nodes[1].id, "B")
        self.assertEqual(nodes[1].label, "Process")
        self.assertEqual(nodes[2].id, "C")
        self.assertEqual(nodes[2].label, "End")
        
        # Check the edges
        self.assertEqual(edges[0].source, "A")
        self.assertEqual(edges[0].target, "B")
        self.assertEqual(edges[1].source, "B")
        self.assertEqual(edges[1].target, "C")
    
    def test_parse_sequence_mermaid(self):
        """Test parsing sequence diagram Mermaid code."""
        # Create a sequence diagram
        mermaid_code = "sequenceDiagram\n    participant User\n    participant System\n    User->>System: Request\n    System-->>User: Response"
        
        # Parse the sequence diagram
        actors, messages = self.flowchart_view._parse_sequence_mermaid(mermaid_code)
        
        # Check the result
        self.assertEqual(len(actors), 2)
        self.assertEqual(len(messages), 2)
        
        # Check the actors
        self.assertEqual(actors[0], "User")
        self.assertEqual(actors[1], "System")
        
        # Check the messages
        self.assertEqual(messages[0]["source"], "User")
        self.assertEqual(messages[0]["target"], "System")
        self.assertEqual(messages[0]["message"], "Request")
        self.assertEqual(messages[1]["source"], "System")
        self.assertEqual(messages[1]["target"], "User")
        self.assertEqual(messages[1]["message"], "Response")
    
    def test_parse_state_machine_mermaid(self):
        """Test parsing state machine diagram Mermaid code."""
        # Create a state machine diagram
        mermaid_code = "stateDiagram\n    [*] --> Idle\n    Idle --> Active: Start\n    Active --> Idle: Stop\n    Active --> [*]: End"
        
        # Parse the state machine diagram
        states, transitions = self.flowchart_view._parse_state_machine_mermaid(mermaid_code)
        
        # Check the result
        self.assertEqual(len(states), 2)
        self.assertEqual(len(transitions), 4)
        
        # Check the states
        self.assertEqual(states[0], "Idle")
        self.assertEqual(states[1], "Active")
        
        # Check the transitions
        self.assertEqual(transitions[0]["source"], "[*]")
        self.assertEqual(transitions[0]["target"], "Idle")
        self.assertEqual(transitions[1]["source"], "Idle")
        self.assertEqual(transitions[1]["target"], "Active")
        self.assertEqual(transitions[1]["label"], "Start")
        self.assertEqual(transitions[2]["source"], "Active")
        self.assertEqual(transitions[2]["target"], "Idle")
        self.assertEqual(transitions[2]["label"], "Stop")
        self.assertEqual(transitions[3]["source"], "Active")
        self.assertEqual(transitions[3]["target"], "[*]")
        self.assertEqual(transitions[3]["label"], "End")
    
    def test_parse_component_mermaid(self):
        """Test parsing component diagram Mermaid code."""
        # Create a component diagram
        mermaid_code = "classDiagram\n    class Frontend\n    class Backend\n    class Database\n    Frontend --> Backend\n    Backend --> Database"
        
        # Parse the component diagram
        components, relationships = self.flowchart_view._parse_component_mermaid(mermaid_code)
        
        # Check the result
        self.assertEqual(len(components), 3)
        self.assertEqual(len(relationships), 2)
        
        # Check the components
        self.assertEqual(components[0]["name"], "Frontend")
        self.assertEqual(components[0]["type"], "component")
        self.assertEqual(components[1]["name"], "Backend")
        self.assertEqual(components[1]["type"], "component")
        self.assertEqual(components[2]["name"], "Database")
        self.assertEqual(components[2]["type"], "component")
        
        # Check the relationships
        self.assertEqual(relationships[0]["source"], "Frontend")
        self.assertEqual(relationships[0]["target"], "Backend")
        self.assertEqual(relationships[0]["type"], "uses")
        self.assertEqual(relationships[1]["source"], "Backend")
        self.assertEqual(relationships[1]["target"], "Database")
        self.assertEqual(relationships[1]["type"], "uses")

if __name__ == "__main__":
    unittest.main()