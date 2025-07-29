# src/cosmonaut/cli.py

import typer

# ✅ Step 1: Create the Typer app first
app = typer.Typer(
    name="cosmonaut",
    help="🚀 Explore your digital universe",
    rich_markup_mode="markdown",
)


# ✅ Step 2: Now you can use @app.command()
@app.command()
def version():
    """Show version."""
    print("v0.1.0")


@app.command()
def ssh_connect(
    target: str = typer.Argument(..., help="user@host"),
):
    """Connect via SSH."""
    print(f"Connecting to {target}")


# ✅ Step 3: Entry point (optional)
if __name__ == "__main__":
    app()
