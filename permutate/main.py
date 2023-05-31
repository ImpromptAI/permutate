import typer, os
from pathlib import Path
from .runner import Runner
from typing import Optional
from typing_extensions import Annotated

app = typer.Typer()
default_file_path = Path(f"{os.path.dirname(os.path.abspath(__file__))}/workspace/plugin_test.yaml")


@app.callback()
def callback():
    """
    Permutate is an automated testing framework for LLM Plugins.
    """


@app.command()
def run(
        test_file_path: Annotated[Optional[Path], typer.Argument(help="Plugin test setup file.")] = default_file_path,
        save_to_html: Annotated[bool, typer.Option(help="Save the final report as HTML.",
                                                   rich_help_panel="Customization and Utils")] = True,
        save_to_csv: Annotated[bool, typer.Option(help="Save the final report as csv.",
                                                  rich_help_panel="Customization and Utils")] = False,
        output_directory: Annotated[Optional[Path], typer.Option(help="Directory to save the final report.",
                                                                 rich_help_panel="Customization and Utils")] = None,
):
    """
    Run the permutation job
    """
    if not test_file_path.exists():
        typer.echo(f"File '{test_file_path}' does not exist.")
        raise typer.Exit(code=1)
    if test_file_path.is_dir():
        typer.echo(f"File '{test_file_path}' is a directory. It should be yaml or json file.")
        raise typer.Exit(code=1)
    if test_file_path.suffix != ".json" and test_file_path.suffix != ".yaml" and test_file_path.suffix != ".yml":
        typer.echo(f"File '{test_file_path}' is not a yaml or json file.")
        raise typer.Exit(code=1)
    if output_directory is not None:
        if not output_directory.exists():
            typer.echo(f"Save directory '{output_directory}' does not exist.")
            raise typer.Exit(code=1)
        if not output_directory.is_dir():
            typer.echo(f"Save directory '{output_directory}' is not a directory.")
            raise typer.Exit(code=1)
    else:
        output_directory = f"{os.path.dirname(os.path.abspath(__file__))}/workspace/"

    output_dir = str(output_directory)
    if not output_dir.endswith("/"):
        output_dir = output_dir + "/"
    runner = Runner()
    runner.start(str(test_file_path), output_dir, save_to_html, save_to_csv)
