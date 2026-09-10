import os
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.rule import Rule
from rich.spinner import Spinner
from rich.live import Live
from rich import box

load_dotenv()

from leetcode import fetch_leetcode_stats, save_daily_snapshot, load_history, calculate_progress
from ai_coach import analyze_with_gemini, extract_sections

console = Console()

def show_banner():
    banner = Text()
    banner.append("  ██╗     ███████╗███████╗████████╗ ██████╗ ██████╗ ██████╗ ███████╗\n", style="bold yellow")
    banner.append("  ██║     ██╔════╝██╔════╝╚══██╔══╝██╔════╝██╔═══██╗██╔══██╗██╔════╝\n", style="bold yellow")
    banner.append("  ██║     █████╗  █████╗     ██║   ██║     ██║   ██║██║  ██║█████╗  \n", style="bold yellow")
    banner.append("  ██║     ██╔══╝  ██╔══╝     ██║   ██║     ██║   ██║██║  ██║██╔══╝  \n", style="bold yellow")
    banner.append("  ███████╗███████╗███████╗   ██║   ╚██████╗╚██████╔╝██████╔╝███████╗\n", style="bold yellow")
    banner.append("  ╚══════╝╚══════╝╚══════╝   ╚═╝    ╚═════╝ ╚═════╝ ╚═════╝╚══════╝\n", style="bold yellow")
    banner.append("\n         🤖  AI Coach — Powered by Gemini\n", style="bold cyan")
    console.print(Panel(banner, border_style="yellow", padding=(0, 2)))

def main():
    show_banner()
    username = console.input("[bold cyan]Enter your LeetCode username: [/bold cyan]").strip()
    if not username:
        console.print("[red]No username provided. Exiting.[/red]")
        return

    with Live(Spinner("dots", text="[cyan]Fetching stats...[/cyan]"), console=console, refresh_per_second=10):
        stats = fetch_leetcode_stats(username)

    if not stats:
        console.print(f"[red]User '{username}' not found.[/red]")
        return

    save_daily_snapshot(stats)
    history  = load_history()
    progress = calculate_progress(history)

    console.print(Rule("[bold cyan]📊 Stats[/bold cyan]"))
    t = Table(box=box.ROUNDED, border_style="cyan", header_style="bold cyan", show_lines=True)
    t.add_column("Difficulty"); t.add_column("Solved"); t.add_column("New")
    t.add_row("🟢 Easy",   str(stats["solved"]["easy"]),   f"+{progress['new_easy']}")
    t.add_row("🟡 Medium", str(stats["solved"]["medium"]), f"+{progress['new_medium']}")
    t.add_row("🔴 Hard",   str(stats["solved"]["hard"]),   f"+{progress['new_hard']}")
    console.print(t)

    run_ai = console.input("\n[bold magenta]🤖 Run AI analysis? [y/n]: [/bold magenta]").strip().lower()
    if run_ai == "y":
        with Live(Spinner("dots", text="[cyan]Gemini thinking...[/cyan]"), console=console, refresh_per_second=10):
            ai_response = analyze_with_gemini(stats, history, progress)
        sections = extract_sections(ai_response)
        console.print(Panel(sections["analysis"],      title="📋 Analysis",      border_style="cyan"))
        console.print(Panel(sections["weak_areas"],    title="⚠️ Weak Areas",    border_style="red"))
        console.print(Panel(sections["practice_plan"], title="📅 Practice Plan", border_style="green"))

    console.print(Rule("[bold yellow]🚀 Happy Coding![/bold yellow]"))

if __name__ == "__main__":
    main()
