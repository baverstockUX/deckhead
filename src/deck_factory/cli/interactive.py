"""
Interactive CLI for Deckhead.

Provides step-by-step user interface with progress tracking,
question prompts, and beautiful terminal output using rich library.
"""

from pathlib import Path
from typing import List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
from rich.table import Table
from rich import print as rprint

from ..core.models import (
    BrandAssets,
    DeckStructure,
    ClarificationQuestion,
    ClarificationResponse
)


class InteractiveCLI:
    """
    Interactive command-line interface.

    Guides users through the deck generation process with
    rich terminal output and progress tracking.
    """

    def __init__(self):
        """Initialize CLI with rich console."""
        self.console = Console()

    def welcome(self) -> None:
        """Display welcome message."""
        self.console.print()
        self.console.print(Panel.fit(
            "[bold cyan]Welcome to Deckhead[/bold cyan]\n"
            "[dim]AI-Powered PowerPoint Generator[/dim]",
            border_style="cyan"
        ))
        self.console.print()

    def prompt_content_file(self) -> Path:
        """
        Prompt user for content file path.

        Returns:
            Path to content file

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        self.console.print("[bold]Step 1/5:[/bold] Content Input", style="cyan")
        self.console.print()

        while True:
            file_path_str = Prompt.ask(
                "Enter path to content file (.md or .txt)",
                default="./content.md"
            )

            file_path = Path(file_path_str).expanduser().resolve()

            if file_path.exists() and file_path.is_file():
                # Check file extension
                if file_path.suffix.lower() not in ['.md', '.txt', '.markdown']:
                    self.console.print(
                        f"[yellow]Warning:[/yellow] File extension {file_path.suffix} not typical for content files. "
                        "Supported: .md, .txt, .markdown"
                    )
                    if not Confirm.ask("Continue anyway?", default=False):
                        continue

                # Display file info
                file_size = file_path.stat().st_size
                self.console.print(
                    f"[green]✓[/green] Loaded: {file_path.name} ({file_size:,} bytes)"
                )
                self.console.print()
                return file_path

            else:
                self.console.print(
                    f"[red]✗[/red] File not found: {file_path}",
                    style="red"
                )
                self.console.print("Please check the path and try again.")
                self.console.print()

    def prompt_brand_assets(self) -> BrandAssets:
        """
        Prompt user for optional brand assets.

        Returns:
            BrandAssets object (may be empty)
        """
        self.console.print("[bold]Step 2/5:[/bold] Brand Assets (Optional)", style="cyan")
        self.console.print()

        has_brand_assets = Confirm.ask(
            "Add brand reference images for style consistency?",
            default=False
        )

        if not has_brand_assets:
            self.console.print("[dim]Skipping brand assets[/dim]")
            self.console.print()
            return BrandAssets()

        # Prompt for image paths
        self.console.print(
            "Enter directory path or comma-separated image file paths:"
        )
        paths_input = Prompt.ask("Paths")

        reference_images = []

        # Check if it's a directory
        input_path = Path(paths_input).expanduser().resolve()
        if input_path.is_dir():
            # Load all images from directory
            for ext in ['*.jpg', '*.jpeg', '*.png', '*.webp']:
                reference_images.extend(input_path.glob(ext))
                reference_images.extend(input_path.glob(ext.upper()))
        else:
            # Parse comma-separated paths
            for path_str in paths_input.split(','):
                path = Path(path_str.strip()).expanduser().resolve()
                if path.exists() and path.is_file():
                    reference_images.append(path)
                else:
                    self.console.print(
                        f"[yellow]Warning:[/yellow] File not found: {path}",
                        style="yellow"
                    )

        if reference_images:
            self.console.print(
                f"[green]✓[/green] Loaded {len(reference_images)} brand image(s):"
            )
            for img in reference_images:
                self.console.print(f"  • {img.name}", style="dim")
        else:
            self.console.print(
                "[yellow]No valid images found. Continuing without brand assets.[/yellow]"
            )

        self.console.print()
        return BrandAssets(reference_images=reference_images)

    def show_parsing_progress(self) -> None:
        """Show progress indicator for content parsing."""
        self.console.print("[bold]Step 3/5:[/bold] Parsing Content", style="cyan")
        self.console.print()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Analyzing content with AI...", total=None)
            return progress, task

    def show_structure_summary(self, structure: DeckStructure) -> None:
        """
        Display parsed structure summary.

        Args:
            structure: Parsed deck structure
        """
        self.console.print(
            f"[green]✓[/green] Found structure for {structure.total_slides} slides"
        )
        self.console.print()

        # Create summary table
        table = Table(title="Deck Structure", show_header=True, header_style="bold cyan")
        table.add_column("Slide", style="dim", width=6)
        table.add_column("Title")
        table.add_column("Content", style="dim")

        for slide in structure.slides[:10]:  # Show first 10
            table.add_row(
                f"#{slide.slide_number}",
                slide.title or "[no title]",
                slide.content_summary[:50] + "..." if len(slide.content_summary) > 50 else slide.content_summary
            )

        if structure.total_slides > 10:
            table.add_row("...", f"({structure.total_slides - 10} more slides)", "")

        self.console.print(table)
        self.console.print()

    def display_clarifications(
        self,
        questions: List[ClarificationQuestion]
    ) -> List[ClarificationResponse]:
        """
        Display clarification questions and collect answers.

        Args:
            questions: List of clarification questions

        Returns:
            List of user responses
        """
        if not questions:
            return []

        self.console.print("[bold]Step 4/5:[/bold] Clarification Questions", style="cyan")
        self.console.print()
        self.console.print(
            f"The AI has {len(questions)} question(s) to improve your deck:"
        )
        self.console.print()

        responses = []

        for i, question in enumerate(questions, 1):
            # Display question with category
            category_color = {
                "structure": "blue",
                "style": "magenta",
                "brand": "yellow",
                "content": "green"
            }.get(question.category, "white")

            self.console.print(
                f"[bold]Question {i}/{len(questions)}[/bold] [{category_color}][{question.category.upper()}][/{category_color}]"
            )
            self.console.print(f"{question.question}")
            self.console.print()

            # Display options if multiple choice
            if question.options:
                for j, option in enumerate(question.options, 1):
                    self.console.print(f"  {j}. {option}")
                self.console.print()

            # Get answer
            while True:
                if question.options:
                    answer = Prompt.ask(
                        "Your answer (number or text)",
                        default="1" if not question.required else None
                    )

                    # Handle numeric selection
                    if answer.isdigit():
                        idx = int(answer) - 1
                        if 0 <= idx < len(question.options):
                            answer = question.options[idx]
                        else:
                            self.console.print(
                                f"[red]Invalid option. Please select 1-{len(question.options)}[/red]"
                            )
                            continue
                else:
                    answer = Prompt.ask(
                        "Your answer",
                        default=None if question.required else "skip"
                    )

                # Validate answer
                if not answer or answer.lower() == "skip":
                    if question.required:
                        self.console.print(
                            "[red]This question is required. Please provide an answer.[/red]"
                        )
                        continue
                    else:
                        self.console.print("[dim]Skipped[/dim]")
                        break

                # Create response
                response = ClarificationResponse(
                    question_id=question.question_id,
                    answer=answer
                )
                responses.append(response)
                self.console.print(f"[green]✓[/green] Recorded: {answer}")
                break

            self.console.print()

        return responses

    def confirm_generation(self, structure: DeckStructure) -> bool:
        """
        Display final structure and confirm generation.

        Args:
            structure: Final deck structure

        Returns:
            True if user confirms, False otherwise
        """
        self.console.print("[bold]Step 5/5:[/bold] Generation", style="cyan")
        self.console.print()

        # Display final structure
        self.console.print(Panel(
            f"[bold]Deck:[/bold] {structure.deck_title}\n"
            f"[bold]Slides:[/bold] {structure.total_slides}\n\n"
            f"[dim]Slide topics:[/dim]\n" +
            "\n".join([f"  • Slide {s.slide_number}: {s.title or s.content_summary[:40]}"
                      for s in structure.slides[:5]]) +
            (f"\n  • ... and {structure.total_slides - 5} more" if structure.total_slides > 5 else ""),
            title="Final Structure",
            border_style="cyan"
        ))
        self.console.print()

        return Confirm.ask(
            f"Generate {structure.total_slides} images and create presentation?",
            default=True
        )

    def show_image_generation_progress(self, total: int):
        """
        Show progress bar for image generation with elapsed time.

        Args:
            total: Total number of images to generate

        Returns:
            Progress context manager
        """
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            console=self.console
        )

    def display_success(self, output_path: Path, generation_time: float) -> None:
        """
        Display success message.

        Args:
            output_path: Path to generated presentation
            generation_time: Total generation time in seconds
        """
        self.console.print()
        self.console.print(Panel.fit(
            f"[bold green]Success![/bold green]\n\n"
            f"Deck saved to: [cyan]{output_path}[/cyan]\n"
            f"Generated in: [yellow]{generation_time:.1f} seconds[/yellow]",
            border_style="green"
        ))
        self.console.print()

        # Ask if user wants to open the file
        if Confirm.ask("Open presentation now?", default=True):
            import subprocess
            import sys

            if sys.platform == "darwin":  # macOS
                subprocess.run(["open", str(output_path)])
            elif sys.platform == "win32":  # Windows
                subprocess.run(["start", str(output_path)], shell=True)
            else:  # Linux
                subprocess.run(["xdg-open", str(output_path)])

    def display_error(self, error: Exception) -> None:
        """
        Display error message.

        Args:
            error: Exception that occurred
        """
        self.console.print()
        self.console.print(Panel(
            f"[bold red]Error:[/bold red]\n\n{str(error)}",
            border_style="red"
        ))
        self.console.print()
