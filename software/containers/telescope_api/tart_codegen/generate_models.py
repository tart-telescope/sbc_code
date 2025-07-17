#!/usr/bin/env python3
"""
Schema to Python model generation script.
Generates Python models from JSON schemas using datamodel-code-generator.
"""

import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


def generate_single_model(schema_file):
    """Generate a single model file from a schema."""
    output_dir = Path("/app/tart_api/generated_models")
    output_filename = schema_file.stem + "_models.py"
    output_path = output_dir / output_filename

    # Build datamodel-codegen command
    cmd = [
        "datamodel-codegen",
        "--input",
        str(schema_file),
        "--output",
        str(output_path),
        "--input-file-type",
        "jsonschema",
        "--output-model-type",
        "pydantic_v2.BaseModel",
        "--field-constraints",
        "--snake-case-field",
        "--target-python-version",
        "3.13",
        "--use-annotated",
        "--use-union-operator",
        "--use-schema-description",
        "--use-field-description",
        "--strip-default-none",
        "--enable-version-header",
        "--use-standard-collections",
        "--formatters",
        "ruff-format",
        "ruff-check",
    ]

    try:
        # Run the command
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        return True, output_filename, None
    except subprocess.CalledProcessError as e:
        return False, output_filename, e.stderr


def add_do_not_edit_headers(output_dir):
    """Add DO NOT EDIT headers to all generated Python files."""
    header = "# DO NOT EDIT! This file is auto-generated from JSON schemas.\n# To make changes, edit the schema files and regenerate.\n\n"

    for py_file in output_dir.glob("*.py"):
        if py_file.name == "__init__.py":
            continue  # Skip __init__.py

        with open(py_file, "r") as f:
            content = f.read()

        # Add header if not already present
        if not content.startswith("# DO NOT EDIT!"):
            with open(py_file, "w") as f:
                f.write(header + content)


def generate_models():
    """Generate Python models from JSON schemas - common first, then others in parallel."""

    # Define paths
    schemas_dir = Path("/app/schemas")
    output_dir = Path("/app/tart_api/generated_models")

    # Ensure output directory exists
    output_dir.mkdir(exist_ok=True)

    # Check if schemas directory exists
    if not schemas_dir.exists():
        print(f"Error: Schemas directory not found at {schemas_dir}")
        sys.exit(1)

    # Find all JSON schema files
    schema_files = list(schemas_dir.glob("**/*.json"))

    if not schema_files:
        print("No JSON schema files found in the schemas directory")
        sys.exit(1)

    print(f"Found {len(schema_files)} schema files")

    # Separate common schema from others
    common_schema = None
    other_schemas = []

    for schema_file in schema_files:
        if schema_file.name == "common.json":
            common_schema = schema_file
        else:
            other_schemas.append(schema_file)

    success_count = 0
    error_count = 0

    # Step 1: Generate common schema first (if it exists)
    if common_schema:
        print("Step 1: Generating common schema first...")
        success, output_filename, error = generate_single_model(common_schema)
        if success:
            print(f"✓ Generated {output_filename}")
            success_count += 1
        else:
            print(f"✗ Error generating {output_filename}:")
            print(f"  Error: {error}")
            error_count += 1
            print("⚠️ Common schema failed - continuing anyway")
    else:
        print("ℹ️ No common.json schema found")

    # Step 2: Process remaining files in parallel
    if other_schemas:
        print("Step 2: Processing remaining schemas in parallel...")

        with ThreadPoolExecutor(max_workers=10) as executor:
            # Submit all tasks
            future_to_file = {
                executor.submit(generate_single_model, schema_file): schema_file
                for schema_file in other_schemas
            }

            # Process results as they complete
            for future in as_completed(future_to_file):
                schema_file = future_to_file[future]
                try:
                    success, output_filename, error = future.result()
                    if success:
                        print(f"✓ Generated {output_filename}")
                        success_count += 1
                    else:
                        print(f"✗ Error generating {output_filename}:")
                        print(f"  Error: {error}")
                        error_count += 1
                except Exception as e:
                    print(f"✗ Unexpected error processing {schema_file.name}: {e}")
                    error_count += 1

    print(f"\nCompleted: {success_count} successful, {error_count} errors")

    # Generate combined __init__.py file
    init_file = output_dir / "__init__.py"
    with open(init_file, "w") as f:
        f.write('"""Generated models from JSON schemas."""\n\n')

        # Import all generated models
        for schema_file in schema_files:
            module_name = schema_file.stem + "_models"
            f.write(f"from .{module_name} import *\n")

    print(f"\n✓ All models generated in {output_dir}")
    print("✓ Created __init__.py with imports")

    # Add DO NOT EDIT message to all generated files
    print("✓ Adding DO NOT EDIT headers...")
    add_do_not_edit_headers(output_dir)

    # List generated files
    generated_files = list(output_dir.glob("*.py"))
    print(f"\nGenerated files ({len(generated_files)}):")
    for file in sorted(generated_files):
        print(f"  - {file.name}")


if __name__ == "__main__":
    generate_models()
