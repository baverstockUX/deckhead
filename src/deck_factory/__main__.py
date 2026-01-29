"""
Main entry point for Deckhead.

Orchestrates the complete deck generation workflow:
1. Load configuration and initialize components
2. Prompt user for content file and brand assets
3. Parse content with AI
4. Ask clarification questions
5. Generate images in parallel
6. Assemble PowerPoint presentation
"""

import asyncio
import sys
import time
from pathlib import Path

from .core.config import ConfigLoader
from .core.models import ImageGenerationRequest, BrandAssets
from .core.exceptions import (
    DeckFactoryError,
    MissingAPIKeyError,
    InvalidAPIKeyError,
    ConfigError
)
from .ai.gemini_client import GeminiClient
from .ai.content_parser import ContentParser
from .ai.clarifier import Clarifier
from .ai.image_factory import ImageFactory
from .deck.assembler import DeckAssembler
from .cli.interactive import InteractiveCLI


async def main():
    """Main application workflow."""
    cli = InteractiveCLI()
    start_time = time.time()

    try:
        # Welcome
        cli.welcome()

        # Select text content mode
        text_mode = cli.prompt_mode_selection()

        # Load configuration
        try:
            config = ConfigLoader.from_env()
        except (MissingAPIKeyError, InvalidAPIKeyError) as e:
            cli.display_error(e)
            cli.console.print(
                "[yellow]Tip:[/yellow] Make sure you have a .env file with your Gemini API key.\n"
                "Example: gemini_key='your-api-key-here'"
            )
            sys.exit(1)
        except ConfigError as e:
            cli.display_error(e)
            sys.exit(1)

        # Initialize components
        gemini_client = GeminiClient(
            api_key=config.gemini_api_key,
            max_concurrent=config.max_concurrent_images
        )
        content_parser = ContentParser(gemini_client, mode=text_mode)
        clarifier = Clarifier(gemini_client)
        image_factory = ImageFactory(gemini_client, config.max_concurrent_images)
        deck_assembler = DeckAssembler()

        # Step 1: Prompt for content file
        content_file = cli.prompt_content_file()

        # Load content
        with open(content_file, 'r', encoding='utf-8') as f:
            content = f.read()

        if not content.strip():
            cli.display_error(Exception("Content file is empty"))
            sys.exit(1)

        # Step 2: Prompt for brand assets
        brand_assets = cli.prompt_brand_assets()

        # Step 3: Parse content
        cli.console.print("[bold]Step 3/5:[/bold] Parsing Content", style="cyan")
        cli.console.print()

        with cli.console.status("[bold green]Analyzing content with AI...") as status:
            deck_structure, clarification_questions = await content_parser.parse_content(content)

        cli.show_structure_summary(deck_structure)

        # Step 4: Clarification questions
        clarifications = []
        if clarification_questions:
            clarifications = cli.display_clarifications(clarification_questions)

            # Refine structure if there are clarifications
            if clarifications:
                cli.console.print("[dim]Refining structure based on your answers...[/dim]")
                with cli.console.status("[bold green]Refining...") as status:
                    deck_structure = await content_parser.refine_structure(
                        deck_structure,
                        clarifications
                    )
                cli.console.print("[green]✓[/green] Structure refined")
                cli.console.print()

        # Step 5: Confirm generation
        if not cli.confirm_generation(deck_structure):
            cli.console.print("[yellow]Generation cancelled by user[/yellow]")
            sys.exit(0)

        # Generate images
        cli.console.print("[bold]Generating images...[/bold]")

        # Create image generation requests
        image_requests = [
            ImageGenerationRequest(
                slide_number=slide.slide_number,
                prompt=slide.image_prompt,
                aspect_ratio="16:9",
                infographic_style=getattr(slide, 'infographic_style', False),
                layout_type=slide.layout_type,
                text_content=slide.text_content
            )
            for slide in deck_structure.slides
        ]

        # Show time estimate
        estimated_time = image_factory.estimate_generation_time(len(image_requests))
        cli.console.print(
            f"[dim]Estimated time: ~{estimated_time:.0f} seconds "
            f"({len(image_requests)} images, {image_factory.max_concurrent} concurrent)[/dim]"
        )
        cli.console.print()

        # Generate images with progress bar
        with cli.show_image_generation_progress(len(image_requests)) as progress:
            task = progress.add_task(
                f"Generating images (0/{len(image_requests)})...",
                total=len(image_requests)
            )

            # Track completed count
            completed = [0]

            def progress_callback(slide_num, total):
                completed[0] += 1
                progress.update(
                    task,
                    advance=1,
                    description=f"Generating images ({completed[0]}/{total})..."
                )

            images = await image_factory.generate_images(
                image_requests,
                brand_assets,
                progress_callback=progress_callback
            )

        cli.console.print(f"[green]✓[/green] Generated {len(images)} images")
        cli.console.print()

        # Assemble presentation
        cli.console.print("[bold]Assembling presentation...[/bold]")

        # Determine output path
        output_filename = deck_structure.deck_title.replace(" ", "_") + ".pptx"
        output_path = config.output_dir / output_filename

        with cli.console.status("[bold green]Building slides...") as status:
            final_path = deck_assembler.create_deck(
                deck_structure,
                images,
                output_path
            )

        # Calculate generation time
        generation_time = time.time() - start_time

        # Success!
        cli.display_success(final_path, generation_time)

    except DeckFactoryError as e:
        cli.display_error(e)
        sys.exit(1)
    except KeyboardInterrupt:
        cli.console.print("\n[yellow]Cancelled by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        cli.display_error(e)
        cli.console.print("[dim]For support, please report this error at:[/dim]")
        cli.console.print("[dim]https://github.com/yourusername/deck-factory/issues[/dim]")
        sys.exit(1)


def cli_main():
    """CLI entry point wrapper."""
    # Run async main
    asyncio.run(main())


if __name__ == "__main__":
    cli_main()
