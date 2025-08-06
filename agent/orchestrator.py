import os
import getpass
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from langchain_tavily import TavilySearch
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import MemorySaver
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.tools import search_jobs_tool

# Load environment variables
load_dotenv()

# LangSmith configuration for tracing and debugging
# API keys are loaded from .env file by load_dotenv()
os.environ["LANGSMITH_TRACING"] = "true"

# Create the agent
memory = MemorySaver()
model = ChatOpenAI(
    model="gpt-4o-mini",  
    temperature=0.1
)
# model = init_chat_model("gpt-4o-mini", model_provider="openai")

search = TavilySearch(max_results=2)
#search_results = search.invoke("What is the weather in SF")
#print(search_results)

# Start with no tools - just conversational agent
tools = [search_jobs_tool, search]
agent_executor = create_react_agent(model, tools, checkpointer=memory)


model_with_tools = model.bind_tools(tools)

if __name__ == "__main__":
    
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
            # # Only print AI messages, skip tool messages
            # if step["messages"][-1].type == "ai":
            #     print(step["messages"][-1].content)
            step["messages"][-1].pretty_print()

