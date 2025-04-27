"""Command-line interface for the Qntropy application."""

import logging
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.logging import RichHandler

from qntropy.importers.cointracking import CointrackingImporter
from qntropy.utils.exceptions import CSVFormatException, DataValidationException

app = typer.Typer(
    name="qntropy",
    help="A cryptocurrency tax reporting tool for Spanish investors",
    add_completion=False,
)

console = Console()
error_console = Console(stderr=True)


def setup_logging(verbose: bool) -> None:
    """
    Set up logging configuration.
    
    Args:
        verbose: Whether to enable verbose logging.
    """
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)],
    )


@app.command()
def import_cointracking(
    file_path: Path = typer.Argument(
        Path("data/input/CoinTracking_Trade_Table_Full.csv"), 
        exists=True, 
        file_okay=True, 
        dir_okay=False, 
        readable=True, 
        help="Path to the Cointracking.info CSV file"
    ),
    output_path: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Path to save the imported transactions (JSON format)"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
):
    """
    Import transactions from a Cointracking.info CSV file.
    """
    setup_logging(verbose)
    
    try:
        importer = CointrackingImporter()
        transactions = importer.import_file(file_path)
        
        console.print(f"Successfully imported [green]{len(transactions)}[/green] transactions from {file_path}")
        
        # If an output path is specified, save the transactions to a JSON file
        if output_path:
            import json
            from qntropy.utils.serializers import TransactionEncoder
            
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as f:
                json.dump([t.model_dump() for t in transactions], f, cls=TransactionEncoder, indent=2)
            console.print(f"Saved transactions to [green]{output_path}[/green]")
        
        return transactions
    
    except CSVFormatException as e:
        error_console.print(f"[bold red]CSV Format Error:[/bold red] {str(e)}")
        sys.exit(1)
    except DataValidationException as e:
        error_console.print(f"[bold red]Data Validation Error:[/bold red] {str(e)}")
        sys.exit(1)
    except Exception as e:
        error_console.print(f"[bold red]Unexpected Error:[/bold red] {str(e)}")
        if verbose:
            import traceback
            error_console.print(traceback.format_exc())
        sys.exit(1)


@app.command()
def version():
    """Display the Qntropy version."""
    import pkg_resources
    
    try:
        version = pkg_resources.get_distribution("qntropy").version
        console.print(f"Qntropy version: [green]{version}[/green]")
    except pkg_resources.DistributionNotFound:
        console.print("Qntropy version: [yellow]development[/yellow]")


if __name__ == "__main__":
    app()