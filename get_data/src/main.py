from rich.console import Console
from rich.prompt import Prompt
import json
from modules.europePMC_utils import search_europe_pmc
from modules.googleScholar_utils import search_google_scholar
from modules.menu_utils import display_menu
from modules.pubmed_utils import search_pubmed
from modules.semanticscholar_utils import search_semanticscholar
from modules.wikipedia_utils import search_wikipedia


def search_and_print(source, func, query, max_articles=1, year_range=(2020, 2025)):
    """Performs the search and prints the results."""
    console = Console()
    console.print(f"\n[bold cyan]🔎 Searching on {source}...[/bold cyan]")
    results = func(query) if source == "Wikipedia" else func(query, max_articles, year_range)
    
    if source == "Wikipedia" and results:
        console.print(f"\n[bold yellow]📖 Wikipedia: {results['title']}[/bold yellow]")
        console.print(f"🔗 [blue]{results['url']}[/blue]")
        console.print(f"📝 {results['summary']}")
    
    return results

def main():
    """Runs searches based on user choice."""
    console = Console()
    with open("keywords.json", "r", encoding="utf-8") as f:
        keywords_by_topic = json.load(f)
    
    sources = {
        "1": ("PubMed", search_pubmed),
        "2": ("Europe PMC", search_europe_pmc),
        "3": ("Semantic Scholar", search_semanticscholar),
        "4": ("Wikipedia", search_wikipedia),
        "5": ("Google Scholar", search_google_scholar),
        "6": ("All Sources", None)
    }
    
    while True:
        choice = display_menu()
        if choice.lower() == 'q':
            console.print("\n[bold red]🚪 Exiting...[/bold red]")
            break
        elif choice in sources:
            max_articles = int(Prompt.ask("[bold white]How many articles per keyword?[/bold white]", default="1"))
            year_range = (2020, 2025)

            if choice == "6":
                # All sources (except Wikipedia)
                for topic, keywords in keywords_by_topic.items():
                    for keyword in keywords:
                        console.print(f"\n[bold cyan]🔎 Topic: [yellow]{topic}[/yellow] — Keyword: [green]{keyword}[/green][/bold cyan]")
                        for key, (source_name, search_func) in sources.items():
                            if key in ["4", "6"]:
                                continue  # Skip Wikipedia and this "All" key
                            try:
                                search_func(keyword, max_articles, year_range)
                            except Exception as e:
                                console.print(f"[red]❌ Error in {source_name} with '{keyword}': {e}[/red]")
            else:
                # One specific source
                source_name, search_func = sources[choice]
                if source_name == "Wikipedia":
                    console.print("[yellow]Wikipedia is not included in automatic keyword search.[/yellow]")
                    continue

                for topic, keywords in keywords_by_topic.items():
                    for keyword in keywords:
                        console.print(f"\n[bold cyan]🔎 Topic: [yellow]{topic}[/yellow] — Keyword: [green]{keyword}[/green][/bold cyan]")
                        try:
                            search_func(keyword, max_articles, year_range)
                        except Exception as e:
                            console.print(f"[red]❌ Error in {source_name} with '{keyword}': {e}[/red]")
        else:
            console.print("\n[bold red]❌ Invalid choice! Please select a valid option.[/bold red]")


if __name__ == "__main__":
    main()