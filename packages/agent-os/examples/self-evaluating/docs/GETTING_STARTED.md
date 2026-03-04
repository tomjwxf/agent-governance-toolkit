# Getting Started with Self-Evolving Agent Framework

Welcome! This guide will help you get up and running with the Self-Evolving Agent Framework in just a few minutes.

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/imran-siddique/self-evaluating-agent-sample.git
cd self-evaluating-agent-sample

# Install dependencies
pip install -r requirements.txt

# Or install as a package
pip install -e .
```

### 2. Set Up Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
OPENAI_API_KEY=your_api_key_here
```

### 3. Run Your First Example

```bash
# Test basic functionality (no API key required)
python tests/test_agent.py

# Run a simple agent (requires API key)
python examples/example.py
```

## Project Structure

```
self-evaluating-agent-sample/
├── src/                    # Core framework modules
│   ├── agent.py           # Main agent implementation
│   ├── observer.py        # Asynchronous learning agent
│   ├── telemetry.py       # Event tracking system
│   ├── polymorphic_output.py  # Adaptive output rendering
│   ├── universal_signal_bus.py  # Omni-channel input
│   ├── agent_brokerage.py     # Agent marketplace
│   ├── orchestrator.py        # Workflow management
│   ├── constraint_engine.py   # Safety constraints
│   ├── evaluation_engineering.py  # Test-driven development
│   ├── wisdom_curator.py      # Human-in-the-loop review
│   ├── circuit_breaker.py     # Automated rollout management
│   ├── intent_detection.py    # Conversation intent analysis
│   ├── ghost_mode.py          # Passive observation
│   ├── prioritization.py      # Context prioritization
│   ├── model_upgrade.py       # Model upgrade management
│   └── generative_ui_engine.py  # Dynamic UI generation
│
├── tests/                  # Comprehensive test suite
│   ├── test_agent.py
│   ├── test_telemetry.py
│   ├── test_polymorphic_output.py
│   └── ...                # Tests for all modules
│
├── examples/               # Usage examples
│   ├── example.py                    # Basic usage
│   ├── sample_full_stack_agent.py    # Comprehensive integration
│   ├── sample_monitoring_agent.py    # Real-world monitoring
│   ├── example_polymorphic_output.py
│   ├── example_universal_signal_bus.py
│   └── ...                           # Examples for all features
│
├── docs/                   # Documentation
│   ├── ARCHITECTURE.md
│   ├── POLYMORPHIC_OUTPUT.md
│   ├── UNIVERSAL_SIGNAL_BUS.md
│   └── ...                # Detailed docs for each feature
│
├── README.md              # Main documentation
├── requirements.txt       # Python dependencies
└── setup.py              # Package installation
```

## Core Concepts

### 1. DoerAgent - Fast Execution

The DoerAgent executes tasks quickly without learning overhead:

```python
from src.agent import DoerAgent

# Initialize agent
agent = DoerAgent()

# Execute a task
result = agent.run("What is 10 + 20?")
print(result['response'])
```

### 2. ObserverAgent - Offline Learning

The ObserverAgent processes telemetry events to improve the wisdom database:

```python
from src.observer import ObserverAgent

# Create observer
observer = ObserverAgent()

# Process events from telemetry stream
observer.process_events()
```

### 3. Universal Signal Bus - Accept Any Input

Process input from any source (text, files, logs, audio):

```python
from src.universal_signal_bus import UniversalSignalBus, create_signal_from_log

bus = UniversalSignalBus()

# Ingest a log stream
signal = create_signal_from_log(
    level="ERROR",
    message="Database connection failed",
    service="user-api"
)

context = bus.ingest(signal)
print(f"Priority: {context.priority}")
```

### 4. Polymorphic Output - Adaptive Rendering

Generate output in the most appropriate format:

```python
from src.polymorphic_output import PolymorphicOutputEngine, InputContext

engine = PolymorphicOutputEngine()

# Generate response based on context
response = engine.generate_response(
    data={"metric": "CPU", "value": "95%"},
    input_context=InputContext.MONITORING
)

print(f"Output type: {response.modality}")  # dashboard_widget
```

## Common Use Cases

### Use Case 1: Chat Agent

```python
from src.agent import DoerAgent

agent = DoerAgent()

# Simple Q&A
result = agent.run("What is the current time?")
print(result['response'])

# Calculations
result = agent.run("Calculate 15 * 24 + 100")
print(result['response'])
```

### Use Case 2: IDE Integration

```python
from src.universal_signal_bus import create_signal_from_file_change
from src.agent import DoerAgent

agent = DoerAgent()
bus = UniversalSignalBus()

# Monitor file changes
signal = create_signal_from_file_change(
    file_path="/src/auth.py",
    change_type="modified",
    content_before="password = 'admin'",
    content_after="hashed = bcrypt.hash(password)"
)

context = bus.ingest(signal)
result = agent.run(context.query)
```

### Use Case 3: System Monitoring

```python
from src.ghost_mode import GhostModeObserver
from src.universal_signal_bus import create_signal_from_log

def on_alert(observation):
    print(f"🚨 Alert: {observation.observation}")

observer = GhostModeObserver(
    confidence_threshold=0.7,
    surfacing_callback=on_alert
)

observer.start_observing()

# Feed logs
signal = create_signal_from_log(
    level="CRITICAL",
    message="Service down",
    service="api-gateway"
)

observer.observe_signal({"type": "log_stream", "data": signal})
```

### Use Case 4: Agent Marketplace

```python
from src.agent_brokerage import AgentMarketplace, AgentBroker

# Create marketplace
marketplace = AgentMarketplace()

# Register agents (see example_agent_brokerage.py for details)
# ...

# Create broker
broker = AgentBroker(marketplace)

# Execute task with automatic agent selection
result = broker.execute_task(
    task="Extract text from PDF",
    selection_strategy="best_value",
    user_constraints={"max_budget": 0.05}
)

print(f"Selected: {result['agent_name']}")
print(f"Cost: ${result['actual_cost']:.4f}")
```

## Next Steps

1. **Explore Examples**: Check out the `examples/` directory for comprehensive samples
2. **Read Documentation**: Visit `docs/` for detailed feature documentation
3. **Run Tests**: Execute tests to understand how each module works
4. **Build Your Agent**: Start with a simple use case and expand

## Key Examples to Try

1. **Full Stack Agent** (`examples/sample_full_stack_agent.py`)
   - Demonstrates integration of multiple modules
   - Shows real-world usage patterns

2. **Monitoring Agent** (`examples/sample_monitoring_agent.py`)
   - Real-world system monitoring
   - Ghost Mode passive observation
   - Dashboard widget rendering

3. **Polymorphic Output** (`examples/example_polymorphic_output.py`)
   - Adaptive output rendering
   - Context-aware UI generation

4. **Universal Signal Bus** (`examples/example_universal_signal_bus.py`)
   - Omni-channel input processing
   - Signal normalization

## Running Tests

```bash
# Run all tests
python tests/test_agent.py
python tests/test_telemetry.py
python tests/test_polymorphic_output.py
python tests/test_universal_signal_bus.py
# ... and so on

# Run a specific test
python tests/test_agent.py
```

## Configuration

Key environment variables (in `.env`):

```bash
# Required
OPENAI_API_KEY=your_api_key_here

# Optional - Model Configuration
AGENT_MODEL=gpt-4o-mini
REFLECTION_MODEL=gpt-4o-mini
EVOLUTION_MODEL=gpt-4o-mini

# Optional - Performance
SCORE_THRESHOLD=0.8
MAX_RETRIES=3
```

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Make sure you're running from the project root
   - Ensure all dependencies are installed: `pip install -r requirements.txt`

2. **API Key Errors**
   - Check that `.env` file exists and contains `OPENAI_API_KEY`
   - Verify the API key is valid

3. **File Not Found**
   - Some examples create files like `system_instructions.json` on first run
   - These are expected and will be created automatically

## Getting Help

- **Documentation**: Check the `docs/` directory for detailed guides
- **Examples**: Review `examples/` for usage patterns
- **Issues**: Report bugs on GitHub Issues
- **Tests**: Look at `tests/` to understand expected behavior

## What's Next?

Now that you're set up, you can:

1. **Build a Custom Agent**: Extend DoerAgent with your own tools and logic
2. **Integrate with Your System**: Use Universal Signal Bus to accept input from your application
3. **Add Safety Constraints**: Use Constraint Engineering to add safety guardrails
4. **Deploy to Production**: Use Circuit Breaker for automated rollout management
5. **Enable Learning**: Use Observer for continuous improvement

Happy building! 🚀
