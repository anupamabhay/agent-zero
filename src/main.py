import asyncio
import sys
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.live import Live
from rich.spinner import Spinner
from rich.text import Text
from src.agent.graph import app

console = Console()


async def main():
    console.print(
        Panel.fit(
            "[bold cyan]Agent Zero Initialized[/bold cyan]\n"
            "Your autonomous AI assistant is ready.\n"
            "Type [bold red]'quit'[/bold red] to exit.",
            border_style="bright_blue",
        )
    )

    # Initialize session state
    state = {"messages": [], "step_count": 0}

    while True:
        try:
            user_input = console.input("[bold green]>> [/bold green]")
            if user_input.lower() in ["quit", "exit"]:
                console.print("[bold yellow]Goodbye![/bold yellow]")
                break

            if not user_input.strip():
                continue

            # Update state for new turn
            state["messages"].append(("user", user_input))
            state["step_count"] = 0

            console.print(f"\n[dim]Starting workflow for: {user_input}[/dim]")

            async for event in app.astream(state):
                for key, value in event.items():
                    # Update local state with the results from the graph
                    state.update(value)

                    # Format node header
                    if key == "reason":
                        icon = "🧠"
                        color = "cyan"
                    elif key == "tools":
                        icon = "🛠️"
                        color = "orange3"
                    else:
                        icon = "📍"
                        color = "white"

                    console.print(f"\n[bold {color}]{icon} Node: {key}[/bold {color}]")

                    last_msg = value["messages"][-1]

                    # Handle Tool Calls
                    if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
                        for tool_call in last_msg.tool_calls:
                            console.print(
                                Panel(
                                    f"[bold yellow]Tool:[/bold yellow] {tool_call['name']}\n"
                                    f"[bold yellow]Args:[/bold yellow] {tool_call['args']}",
                                    title="Action Requested",
                                    border_style="yellow",
                                )
                            )

                    # Handle AI Response
                    elif hasattr(last_msg, "content") and last_msg.content:
                        content = last_msg.content

                        # Process Multi-part content
                        if isinstance(content, list):
                            full_text = "".join(
                                part["text"]
                                if isinstance(part, dict) and "text" in part
                                else str(part)
                                for part in content
                            )
                        else:
                            full_text = str(content)

                        if full_text.strip():
                            # Render Markdown in Terminal!
                            console.print(
                                Panel(
                                    Markdown(full_text),
                                    title="Zero Response",
                                    border_style="green",
                                    padding=(1, 2),
                                )
                            )

        except Exception as e:
            if "RESOURCE_EXHAUSTED" in str(e) or "429" in str(e):
                console.print(
                    Panel(
                        "[bold red]Rate Limit Exceeded (429)[/bold red]\n\n"
                        "The Gemini API free tier is busy. Please wait ~30 seconds and try again.\n"
                        "Tip: Once the agent finds your file, it will use fewer tokens.",
                        title="API Limit",
                        border_style="red",
                    )
                )
            else:
                console.print(f"\n[bold red][Error][/bold red] {e}")


if __name__ == "__main__":
    asyncio.run(main())
