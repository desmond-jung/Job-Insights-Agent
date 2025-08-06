from agent.orchestrator import agent_executor

def main():
    config = {"configurable": {"thread_id": "abc123"}}
    
    input_message = {
        "role": "user", 
        "content": "Hi, I'm Bob and I live in SF."
    }
    
    for step in agent_executor.stream(
        {"messages": [input_message]}, config, stream_mode="values"
    ):
        step["messages"][-1].pretty_print()

if __name__ == "__main__":
    main()