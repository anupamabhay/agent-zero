import asyncio
from src.agent.graph import app

async def main():
    print("Hi! I'm Zero, your autonomous AI assistant. How can I help you today? Type 'quit' to exit.")
    
    while True:
        user_input = input(">> ")
        if user_input.lower() in ["quit", "exit"]:
            print("Have a great day!")
            break

        # Initialize the state with user message
        initial_state = {"messages": [("user", user_input)]}

        # Run the agent workflow
        async for event in app.astream(initial_state):
            for key, value in event.items():
                print(f"\n(Node: {key})")

                last_msg = value["messages"][-1]

                if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
                    for tool_call in last_msg.tool_calls:
                        print(f"CALL: {tool_call['name']}")
                        print(f"ARGS: {tool_call['args']}")

                elif hasattr(last_msg, "content") and last_msg.content:
                    content = last_msg.content

                    if isinstance(content, list):
                        full_text = "".join(
                            part["text"] if isinstance(part, dict) and "text" in part
                            else str(part) for part in content
                        )
                        print(f"AI: {full_text}")
                    else:
                        print(f"AI: {content}")

if __name__ == "__main__":
    asyncio.run(main())