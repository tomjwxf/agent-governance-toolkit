"""
Example: Polymorphic Output + Universal Signal Bus Integration

This demonstrates how the Polymorphic Output system integrates with
the Universal Signal Bus to create a complete omni-channel architecture:

- Universal Signal Bus: Normalizes ANY input → Standard ContextObject
- Polymorphic Output: Generates ANY output → Appropriate UI Component

Together: Complete Input-Output Agnostic Architecture
"""

import sys
import os

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.universal_signal_bus import (
    UniversalSignalBus,
    create_signal_from_file_change,
    create_signal_from_log,
    create_signal_from_text
)
from src.polymorphic_output import (
    PolymorphicOutputEngine,
    InputContext
)
from src.generative_ui_engine import GenerativeUIEngine


def print_section(title: str):
    """Print a section header."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def demo_complete_pipeline():
    """
    Demonstrate the complete pipeline:
    Any Input → Signal Bus → Agent → Polymorphic Output → UI Component
    """
    print_section("Complete Omni-Channel Pipeline")
    
    # Initialize systems
    signal_bus = UniversalSignalBus()
    output_engine = PolymorphicOutputEngine()
    ui_engine = GenerativeUIEngine()
    
    # Test cases showing different input→output combinations
    test_cases = [
        {
            "name": "Log Stream → Dashboard Widget",
            "signal": create_signal_from_log(
                level="ERROR",
                message="Database connection pool exhausted",
                error_code="500",
                service="user-api"
            ),
            "agent_response": {
                "metric_name": "DB Connection Errors",
                "metric_value": "15/min",
                "trend": "up",
                "alert_level": "critical"
            }
        },
        {
            "name": "File Change → Ghost Text",
            "signal": create_signal_from_file_change(
                file_path="/workspace/app.py",
                change_type="modified",
                content_before="def calculate(",
                content_after="def calculate_",
                language="python"
            ),
            "agent_response": "total(items: List[float]) -> float:\n    return sum(items)"
        },
        {
            "name": "Text Query → Table",
            "signal": create_signal_from_text("Show me all users"),
            "agent_response": [
                {"id": 1, "name": "Alice", "status": "active"},
                {"id": 2, "name": "Bob", "status": "inactive"}
            ]
        }
    ]
    
    for test_case in test_cases:
        print(f"\n{'─'*70}")
        print(f"Test: {test_case['name']}")
        print(f"{'─'*70}")
        
        # Step 1: Normalize Input
        context_obj = signal_bus.ingest(test_case['signal'])
        print(f"\n1️⃣ Input Normalized:")
        print(f"   Signal Type: {context_obj.signal_type.value}")
        print(f"   Intent: {context_obj.intent}")
        print(f"   Priority: {context_obj.priority}")
        
        # Step 2: Agent Processing (simulated)
        # In real system: agent.run(context_obj.query)
        agent_response = test_case['agent_response']
        print(f"\n2️⃣ Agent Response:")
        print(f"   Type: {type(agent_response).__name__}")
        
        # Step 3: Generate Polymorphic Output
        # Map signal type to input context
        context_mapping = {
            "file_change": InputContext.IDE,
            "log_stream": InputContext.MONITORING,
            "text": InputContext.CHAT
        }
        input_context = context_mapping.get(
            context_obj.signal_type.value,
            InputContext.CHAT
        )
        
        poly_response = output_engine.generate_response(
            data=agent_response,
            input_context=input_context,
            input_signal_type=context_obj.signal_type.value,
            urgency=context_obj.urgency_score
        )
        
        print(f"\n3️⃣ Polymorphic Output:")
        print(f"   Modality: {poly_response.modality.value}")
        
        # Step 4: Generate UI Component
        ui_component = ui_engine.render(poly_response)
        print(f"\n4️⃣ UI Component:")
        print(f"   Component: {ui_component.component_type}")
        print(f"   Props: {list(ui_component.props.keys())[:5]}")
        
        # Show the complete transformation
        print(f"\n✅ Transformation Complete:")
        print(f"   {context_obj.signal_type.value} → {poly_response.modality.value} → {ui_component.component_type}")


def demo_signal_to_component_mapping():
    """Show the mapping from signal types to component types."""
    print_section("Signal Type → UI Component Mapping")
    
    mappings = [
        ("file_change (IDE)", "GhostText", "Inline code suggestions"),
        ("log_stream (ERROR)", "DashboardWidget", "Real-time metric display"),
        ("log_stream (metrics)", "Chart", "Time series visualization"),
        ("text (list query)", "Table", "Sortable data grid"),
        ("text (analysis)", "Card", "Information panel"),
        ("audio_stream (urgent)", "Notification", "Alert toast")
    ]
    
    print("\n" + "─"*70)
    print(f"{'Signal Input':<25} {'UI Output':<20} {'Purpose':<25}")
    print("─"*70)
    
    for signal, component, purpose in mappings:
        print(f"{signal:<25} {component:<20} {purpose:<25}")
    
    print("─"*70)
    
    print("\n💡 Key Insight:")
    print("   The system automatically chooses the right UI component")
    print("   based on the input signal type and data characteristics.")


def demo_backward_compatibility():
    """Show backward compatibility with text-only systems."""
    print_section("Backward Compatibility with Text Systems")
    
    output_engine = PolymorphicOutputEngine()
    
    # Generate a complex response
    response = output_engine.generate_response(
        data=[
            {"name": "Alice", "age": 30, "city": "NYC"},
            {"name": "Bob", "age": 25, "city": "LA"}
        ],
        input_context=InputContext.CHAT
    )
    
    print("\nModern System (with UI):")
    print(f"  Modality: {response.modality.value}")
    print(f"  Component: Table with sorting and filtering")
    
    print("\nLegacy System (text-only):")
    print(f"  Text Fallback:\n{response.text_fallback}")
    
    print("\n✅ Both systems work!")
    print("   Modern apps get rich UI components")
    print("   Legacy apps get formatted text")


def demo_the_vision():
    """Show the complete vision."""
    print_section("🚀 The Complete Vision")
    
    print("""
    ┌─────────────────────────────────────────────────────────────────┐
    │                    THE OMNI-CHANNEL AI SYSTEM                   │
    └─────────────────────────────────────────────────────────────────┘
    
    Input Side: UNIVERSAL SIGNAL BUS
    ├─ File changes from IDE
    ├─ Log streams from servers
    ├─ Audio from meetings
    ├─ API events
    ├─ Clickstream data
    └─ Traditional text
                    ↓
            ┌───────────────┐
            │  NORMALIZER   │  ← Converts everything to ContextObject
            └───────────────┘
                    ↓
            ┌───────────────┐
            │     AGENT     │  ← Processes the request
            └───────────────┘
                    ↓
            ┌───────────────┐
            │ POLYMORPHIC   │  ← Determines response modality
            │    OUTPUT     │
            └───────────────┘
                    ↓
    Output Side: GENERATIVE UI ENGINE
    ├─ Dashboard widgets for monitoring
    ├─ Ghost text for IDE
    ├─ Charts for time series
    ├─ Tables for structured data
    ├─ Notifications for alerts
    └─ Traditional text for chat
    
    The Result:
    ✅ Input can be ANYTHING → Normalized to ContextObject
    ✅ Output can be ANYTHING → Rendered as appropriate UI
    ✅ Agent is COMPLETELY AGNOSTIC to input/output format
    ✅ Developers integrate once, support all modalities
    
    This is the future of AI interaction.
    """)


def main():
    """Run all demonstrations."""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*8 + "OMNI-CHANNEL AI: UNIVERSAL INPUT + POLYMORPHIC OUTPUT" + " "*5 + "║")
    print("╚" + "="*68 + "╝")
    
    print("""
    This demonstrates the complete omni-channel architecture:
    
    Universal Signal Bus (Input Side):
      "The entry point is NOT a UI - it's a Signal Normalizer"
      ANY input → Standard ContextObject
    
    Polymorphic Output (Output Side):
      "If input can be anything, output must be anything"
      Standard response → ANY UI component
    
    Together: Complete Input-Output Agnostic Architecture
    """)
    
    demo_complete_pipeline()
    demo_signal_to_component_mapping()
    demo_backward_compatibility()
    demo_the_vision()
    
    print("\n" + "="*70)
    print("  ✨ Integration demonstration complete!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
