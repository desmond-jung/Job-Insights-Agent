from agent.orchestrator import agent_executor

def main():
    config = {"configurable": {"thread_id": "convo1"}}
    
    # Start of Convo
    print("Job Insights Agent here! Type 'quit' to exit.")

    while True:
        # user input
        user_input = input("\n You: ")

        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("Goodbye!")
            break

        # Create message
        input_message = {"role": "user", "content": user_input}

        # Agent response
        for step in agent_executor.stream(
            {"messages": [input_message]}, config, stream_mode="values", recursion_limit=50
        ):
            # Only print AI messages, skip tool messages
            if step["messages"][-1].type == "ai":
                print(step["messages"][-1].content)

if __name__ == "__main__":
    main()