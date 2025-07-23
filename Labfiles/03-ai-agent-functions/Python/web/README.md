# AI Agent Web Application

This web application provides a web interface for the Azure AI Agent that was originally implemented as a console application in `../agent.py`.

## Features

- Web-based chat interface for interacting with the Azure AI Agent
- Support for custom functions (like submitting support tickets)
- Session-based conversation management
- Real-time messaging with the AI agent

## Prerequisites

1. Python 3.8 or higher
2. Azure AI Services credentials configured
3. An `.env` file in the parent directory with the following variables:
   - `PROJECT_ENDPOINT`: Your Azure AI project endpoint
   - `MODEL_DEPLOYMENT_NAME`: Your model deployment name

## Installation

1. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

2. Ensure the `.env` file exists in the parent directory with proper Azure credentials

3. Make sure you have proper Azure authentication set up (DefaultAzureCredential)

## Running the Application

1. Start the Flask application:
   ```
   python app.py
   ```

2. Open your web browser and navigate to:
   ```
   http://localhost:5000
   ```

3. Start chatting with the AI agent!

## Project Structure

```
web/
├── app.py                 # Main Flask application
├── templates/
│   └── index.html        # Web interface template
├── requirements.txt      # Python dependencies
└── README.md            # This file

../
├── agent.py             # Original console application
├── user_functions.py    # Custom functions for the agent
└── .env                 # Environment variables (not in repo)
```

## API Endpoints

- `GET /`: Main chat interface
- `POST /start_conversation`: Initialize a new conversation thread
- `POST /send_message`: Send a message to the agent
- `GET /get_conversation_history`: Retrieve conversation history
- `POST /clear_conversation`: Clear the current conversation

## Custom Functions

The agent has access to the following custom functions defined in `../user_functions.py`:

- `submit_support_ticket(email_address, description)`: Creates a support ticket with the provided details

## Troubleshooting

1. **Agent initialization fails**: Check that your `.env` file contains the correct Azure credentials and that you have proper authentication configured.

2. **Module import errors**: Ensure that the parent directory containing `agent.py` and `user_functions.py` is accessible and that all required packages are installed.

3. **Connection errors**: Verify your Azure AI Services endpoint and credentials are correct and that you have proper network connectivity.

## Security Notes

- The application uses Flask sessions to manage conversation state
- Make sure to set a proper `SECRET_KEY` environment variable in production
- Azure credentials are handled securely through DefaultAzureCredential
