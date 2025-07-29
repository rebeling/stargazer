# src/cosmonaut/rendering/console.py
from rich.console import Console
from rich.table import Table

console = Console()


def render_specs(target: str, specs: dict):
    """Render specs in a rich table."""
    table = Table(
        "Property", "Value", title=f"📊 System Specs: {target}", border_style="blue"
    )

    for key, value in specs.items():
        value_str = (
            ", ".join(str(item).strip() for item in value if str(item).strip())
            if isinstance(value, (list, tuple))
            else str(value)
            if value is not None
            else "None"
        )

        table.add_row(key, value_str)

    console.print("\n")
    console.print(table)
    console.print("\n")
