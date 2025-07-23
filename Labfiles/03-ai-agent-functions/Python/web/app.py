import os
import sys
from flask import Flask, render_template, request, jsonify, session
from dotenv import load_dotenv
from pathlib import Path
import uuid

# Add parent directory to path to import agent modules
sys.path.append(str(Path(__file__).parent.parent))

from azure.identity import DefaultAzureCredential
from azure.ai.agents import AgentsClient
from azure.ai.agents.models import FunctionTool, ToolSet, MessageRole
from user_functions import user_functions

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Global variables for agent client and configuration
agent_client = None
agent = None
toolset = None

def initialize_agent():
    """Initialize the Azure AI agent client and configuration"""
    global agent_client, agent, toolset
    
    # Load environment variables from parent directory
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(env_path)
    
    project_endpoint = "https://project-blue-resource.services.ai.azure.com/api/projects/project_blue"
    model_deployment = "gpt-4o-mini"
    
    if not project_endpoint:
        raise ValueError("PROJECT_ENDPOINT environment variable is required")
    
    # Connect to the Agent client
    agent_client = AgentsClient(
        endpoint=project_endpoint,
        credential=DefaultAzureCredential(
            exclude_environment_credential=True,
            exclude_managed_identity_credential=True
        )
    )
    
    # Create function tools and toolset
    functions = FunctionTool(user_functions)
    toolset = ToolSet()
    toolset.add(functions)
    
    # Get the agent (using the same ID from the original code)
    agent = agent_client.get_agent("asst_k8ruq73US00cHBI3BHv7ju1c")
    agent_client.enable_auto_function_calls(toolset)

@app.route('/')
def index():
    """Main chat interface"""
    return render_template('index.html')

@app.route('/start_conversation', methods=['POST'])
def start_conversation():
    """Start a new conversation thread"""
    try:
        if not agent_client:
            initialize_agent()
        
        # Create a new thread for this session
        thread = agent_client.threads.create()
        session['thread_id'] = thread.id
        session['conversation_history'] = []
        
        return jsonify({
            'success': True,
            'agent_name': agent.name,
            'agent_id': agent.id,
            'thread_id': thread.id
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/send_message', methods=['POST'])
def send_message():
    """Send a message to the agent"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'success': False, 'error': 'Message cannot be empty'}), 400
        
        thread_id = session.get('thread_id')
        if not thread_id:
            return jsonify({'success': False, 'error': 'No active conversation. Please start a new conversation.'}), 400
        
        # Send message to the agent
        message = agent_client.messages.create(
            thread_id=thread_id,
            role="user",
            content=user_message
        )
        
        # Process the message with the agent
        run = agent_client.runs.create_and_process(thread_id=thread_id, agent_id=agent.id)
        
        # Check for run failures
        if run.status == "failed":
            return jsonify({
                'success': False, 
                'error': f'Agent run failed: {run.last_error}'
            }), 500
        
        # Get the agent's response
        # List all messages and find the last agent message
        messages = agent_client.messages.list(thread_id=thread_id, order="desc", limit=10)
        
        agent_response = ""
        for message in messages:
            if message.role == MessageRole.AGENT and message.text_messages:
                last_msg = message.text_messages[-1]
                agent_response = last_msg.text.value
                break
        
        # Update conversation history in session
        if 'conversation_history' not in session:
            session['conversation_history'] = []
        
        session['conversation_history'].append({
            'user': user_message,
            'agent': agent_response
        })
        
        return jsonify({
            'success': True,
            'agent_response': agent_response,
            'conversation_history': session['conversation_history']
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/get_conversation_history', methods=['GET'])
def get_conversation_history():
    """Get the full conversation history"""
    try:
        thread_id = session.get('thread_id')
        if not thread_id:
            return jsonify({'success': False, 'error': 'No active conversation'}), 400
        
        # Get messages from Azure AI Agents
        messages = agent_client.messages.list(thread_id=thread_id, order="asc")
        
        conversation = []
        for message in messages:
            if message.text_messages:
                last_msg = message.text_messages[-1]
                conversation.append({
                    'role': message.role,
                    'content': last_msg.text.value
                })
        
        return jsonify({
            'success': True,
            'conversation': conversation
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/clear_conversation', methods=['POST'])
def clear_conversation():
    """Clear the current conversation and start fresh"""
    session.pop('thread_id', None)
    session.pop('conversation_history', None)
    return jsonify({'success': True, 'message': 'Conversation cleared'})

if __name__ == '__main__':
    try:
        initialize_agent()
        print(f"Starting web application for agent: {agent.name} ({agent.id})")
        app.run(debug=True, host='0.0.0.0', port=5000)
    except Exception as e:
        print(f"Failed to initialize agent: {e}")
        print("Please check your .env file and Azure credentials")
