import typer
import os
from datetime import date
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from web_crawler.spiders import crawler
from entity_resolution.er import EntityResolutionRunner
import logging

app = typer.Typer(
    rich_markup_mode="rich",
    add_completion=False,
    no_args_is_help=True,
    pretty_exceptions_show_locals=False,
)

today = str(date.today())
DEFAULT_SEARCH_TERM = "X"
DEFAULT_OUT_FILE_DIR = f"tmp/data/{today}"
DEFAULT_OUT_PLOT_DIR = f"tmp/plot/{today}"
DEFAULT_OUT_FILE_NAME = "active_companies"
DEFAULT_OUT_PLOT_FORMAT = "html"
DEFAULT_OUT_FILE_FORMAT = "csv"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] - %(message)s",
    handlers=[logging.StreamHandler()]
)


@app.command("run_crawler")
def run_crawler(
    search_param: str = typer.Option(default=DEFAULT_SEARCH_TERM, help="Provide a value to search for active companies."),
    output_dir: str = typer.Option(default=DEFAULT_OUT_FILE_DIR, help="Provide the output directory name where the file with crawled data has to be stored."),
    output_filename: str = typer.Option(default=DEFAULT_OUT_FILE_NAME, help="Provide the name for the file in which the crawled data has to be stored."),
    output_file_format: str = typer.Option(default=DEFAULT_OUT_FILE_FORMAT, help="Provide the output file format."),
):
    """
    Run the web crawler to collect data on active companies.
    """
    # Get project settings
    settings = get_project_settings()

    # Add custom settings for output file
    settings.set(
        "FEEDS",
        {
            os.path.join(
                f"{output_dir}",
                f"{output_filename}_{search_param}.{output_file_format.lower()}",
            ): {
                "format": output_file_format.lower(),
            },
        },
    )

    # Create a CrawlerProcess with project settings
    process = CrawlerProcess(settings)

    # Add spider to the process
    process.crawl("web_crawler", search_param=search_param)

    # Start the crawling process
    process.start()


@app.command("run_er")
def run_er(
    input_filepath: str = typer.Option(
        default=f"{DEFAULT_OUT_FILE_DIR}/{DEFAULT_OUT_FILE_NAME}_{DEFAULT_SEARCH_TERM}.{DEFAULT_OUT_FILE_FORMAT}",
        help="Provide the full path of the input dataset.",
    ),
    out_plot_path: str = typer.Option(
        default=f"{DEFAULT_OUT_PLOT_DIR}/{DEFAULT_OUT_FILE_NAME}_{DEFAULT_SEARCH_TERM}.{DEFAULT_OUT_PLOT_FORMAT}",
        help="Provide the full path for the output plot visualizating the entity relationships.",
    ),
):
    """
    Run the entity resolution pipeline.
    """
    EntityResolutionRunner(input_filepath, out_plot_path).run_er()


@app.command("view_er_in_browser")
def view_er_in_browser(
    out_plot_path: str = typer.Option(
        default=f"{DEFAULT_OUT_PLOT_DIR}/{DEFAULT_OUT_FILE_NAME}_{DEFAULT_SEARCH_TERM}.{DEFAULT_OUT_PLOT_FORMAT}",
        help="Provide the full path for the output plot visualizating the entity relationships.",
    ),
):
    """
    View the entity resolution graph in a web browser.
    """
    typer.launch(f"index.html")


def main():
    """
    Main entry point for the CLI application.
    """
    app()
