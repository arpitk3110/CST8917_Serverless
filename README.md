# Text Analyzer – Azure Functions with Cosmos DB 

This project is an Azure Functions application that analyzes input text, stores the analysis results in Azure Cosmos DB, and provides an endpoint to retrieve past analysis history.

## Prerequisites
 
Before running this project locally, make sure you have the following installed:

 - Python 3.10+

 - Azure Functions Core Tools v4

 - Visual Studio Code

VS Code Extensions:

 - Azure Functions

 - Azure Account

 - Azurite

### You also need:

 - An Azure subscription 

 - An Azure Cosmos DB account

### Running the Project Locally

1. Clone the repository and open it in VS Code

   - Open the project folder in VS Code.

### 2. Create and configure local.settings.json

Example:

 ```json
{
  "IsEncrypted": false,
  "Values": {
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "DATABASE_CONNECTION_STRING": "<YOUR_COSMOS_DB_CONNECTION_STRING>"
  }
}
 
  - Replace <YOUR_COSMOS_DB_CONNECTION_STRING> with the Primary Connection String from your Azure Cosmos DB account.


### 3. Install Python dependencies

In the project root, run:

  - pip install -r requirements.txt

### 4. Start Azurite (local storage emulator)

In VS Code:

 - Press F1 

 - Select Azurite: Start

Verify Azurite is running from the VS Code status bar.


### 5. Run the Azure Functions app locally

In the terminal, run:

  - func start

You should see output similar to:

  - TextAnalyzer: http://localhost:7071/api/TextAnalyzer

  - GetAnalysisHistory: http://localhost:7071/api/GetAnalysisHistory

## Azure Deployment Notes 

When deployed to Azure:
 
  - The same environment variable name (DATABASE_CONNECTION_STRING) must be added in:
Function App → Configuration → Application Settings

 - After updating settings, the Function App must be restarted 

 

## Security Notes 

  - Do not commit local.settings.json to source control

  - Connection strings are stored securely using Azure Application Settings

  
## Project Structure 

 - function_app.py - Azure Functions implementation

 - requirements.txt – Python dependencies 

 - local.settings.json – Local environment configuration 

 - README.md – Project documentation


## Summary

This project demonstrates:

 - Serverless APIs using Azure Functions (Python)

 - Storing JSON data in Azure Cosmos DB

 - Retrieving historical data via a REST endpoint

 - Local development with VS Code and Azurite

 - Deployment and configuration in Azure