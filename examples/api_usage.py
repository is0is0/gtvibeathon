"""Example usage of the 3DAgency Python API."""

from agency3d import Agency3D, Config
from pathlib import Path


def basic_example():
    """Basic usage example."""
    # Initialize with default config (loads from .env)
    agency = Agency3D()

    # Generate a scene
    result = agency.create_scene("a cozy cyberpunk cafe at sunset")

    if result.success:
        print(f"✓ Render saved to: {result.output_path}")
        print(f"  Iterations: {result.iterations}")
        print(f"  Render time: {result.render_time:.2f}s")
    else:
        print(f"✗ Generation failed: {result.error}")


def custom_config_example():
    """Example with custom configuration."""
    # Create custom config
    config = Config(
        ai_provider="anthropic",
        ai_model="claude-3-5-sonnet-20241022",
        render_samples=256,
        render_engine="CYCLES",
        max_iterations=3,
        enable_reviewer=True,
    )

    # Initialize with custom config
    agency = Agency3D(config)

    # Generate scene
    result = agency.create_scene(
        "a mystical forest clearing with ancient ruins",
        session_name="mystical_forest"
    )

    print(f"Session directory: {result.output_path.parent if result.output_path else 'N/A'}")


def review_disabled_example():
    """Example with reviewer disabled for faster generation."""
    agency = Agency3D()

    # Disable review for this generation
    result = agency.create_scene(
        "a simple geometric composition",
        enable_review=False,
        max_iterations=1
    )

    if result.success:
        print(f"Quick render complete: {result.output_path}")


def batch_generation_example():
    """Generate multiple scenes in a batch."""
    agency = Agency3D()

    prompts = [
        "a cozy cyberpunk cafe at sunset",
        "a futuristic spaceship interior",
        "an underwater coral reef scene",
    ]

    results = []
    for i, prompt in enumerate(prompts, 1):
        print(f"\n[{i}/{len(prompts)}] Generating: {prompt}")

        result = agency.create_scene(
            prompt,
            session_name=f"batch_{i}",
            enable_review=False,
            max_iterations=1
        )

        results.append(result)

        if result.success:
            print(f"  ✓ {result.output_path}")
        else:
            print(f"  ✗ {result.error}")

    # Summary
    successful = sum(1 for r in results if r.success)
    print(f"\n{successful}/{len(results)} scenes generated successfully")


def inspect_results_example():
    """Example of inspecting generation results."""
    agency = Agency3D()

    result = agency.create_scene("a medieval blacksmith workshop")

    if result.success:
        print(f"\n=== Generation Results ===")
        print(f"Prompt: {result.prompt}")
        print(f"Iterations: {result.iterations}")
        print(f"Render time: {result.render_time:.2f}s")
        print(f"\nConcept:")
        print(result.concept)
        print(f"\nScripts generated:")
        for script in result.scripts:
            print(f"  - {script.name}")
        print(f"\nAgent responses: {len(result.agent_responses)}")
        for response in result.agent_responses:
            print(f"  - {response.agent_role.value}: {len(response.content)} chars")


if __name__ == "__main__":
    print("3DAgency API Examples\n")

    # Uncomment the example you want to run:

    # basic_example()
    # custom_config_example()
    # review_disabled_example()
    # batch_generation_example()
    # inspect_results_example()

    print("\nUncomment an example in the code to run it!")
