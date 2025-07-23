import os
from dotenv import load_dotenv
from typing import Any
from pathlib import Path
from azure.identity import DefaultAzureCredential
from azure.ai.agents import AgentsClient
from azure.ai.agents.models import FunctionTool, ToolSet, ListSortOrder, MessageRole, FilePurpose,CodeInterpreterTool,FileSearchTool
from user_functions import user_functions

# Add references

def main(): 

    # Clear the console
    os.system('cls' if os.name=='nt' else 'clear')

    # Load environment variables from .env file
    load_dotenv()
    project_endpoint= os.getenv("PROJECT_ENDPOINT")
    model_deployment = os.getenv("MODEL_DEPLOYMENT_NAME")


    # Connect to the Agent client
    agent_client = AgentsClient(
    endpoint=project_endpoint,
    credential=DefaultAzureCredential
        (exclude_environment_credential=True,
         exclude_managed_identity_credential=True)
    )


    # Define an agent that can use the custom functions
    with agent_client:
        

        # Create file search tool with resources followed by creating agent
        functions = FunctionTool(user_functions)
        toolset = ToolSet()
        toolset.add(functions)
        #agent_client.update_agent(agent_id="asst_k8ruq73US00cHBI3BHv7ju1c",toolset=toolset)
        agent = agent_client.get_agent("asst_k8ruq73US00cHBI3BHv7ju1c")
        agent_client.enable_auto_function_calls(toolset)
        thread = agent_client.threads.create()
        print(f"You're chatting with: {agent.name} ({agent.id})")


    # Loop until the user types 'quit'
        while True:
        # Get input text
            user_prompt = input("Enter a prompt (or type 'quit' to exit): ")
            if user_prompt.lower() == "quit":
                break
            if len(user_prompt) == 0:
                print("Please enter a prompt.")
                continue

            # Send a prompt to the agent
            message = agent_client.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_prompt
            )
            run = agent_client.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)

                    # Check the run status for failures
            if run.status == "failed":
                print(f"Run failed: {run.last_error}")
                    
            # Show the latest response from the agent
            last_msg = agent_client.messages.get_last_message_text_by_role(
                thread_id=thread.id,
                role=MessageRole.AGENT,
            )
            if last_msg:
                print(f"Last Message: {last_msg.text.value}")

                # Get the conversation history
        print("\nConversation Log:\n")
        messages = agent_client.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
        for message in messages:
            if message.text_messages:
                last_msg = message.text_messages[-1]
                print(f"{message.role}: {last_msg.text.value}\n")
        
    



if __name__ == '__main__': 
    main()
