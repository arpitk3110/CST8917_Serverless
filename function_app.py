# =============================================================================
# IMPORTS - Libraries
# =============================================================================
import azure.functions as func
import logging
import json
import re
import os
import uuid
from datetime import datetime

# =============================================================================
# Cosmos DB SDK import
# =============================================================================
from azure.cosmos import CosmosClient, exceptions

# =============================================================================
# CREATE THE FUNCTION APP
# =============================================================================
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# =============================================================================
# Cosmos DB configuration
# =============================================================================
COSMOS_CONNECTION_STRING = os.environ.get("DATABASE_CONNECTION_STRING")

COSMOS_DB_NAME = "TextAnalyzerDB"
COSMOS_CONTAINER_NAME = "AnalysisResults"

cosmos_container = None

if COSMOS_CONNECTION_STRING:
    try:
        cosmos_client = CosmosClient.from_connection_string(COSMOS_CONNECTION_STRING)
        cosmos_database = cosmos_client.get_database_client(COSMOS_DB_NAME)
        cosmos_container = cosmos_database.get_container_client(COSMOS_CONTAINER_NAME)
        logging.info("Connected to Cosmos DB successfully.")
    except Exception as e:
        logging.error(f"Cosmos DB connection failed: {e}")
        cosmos_container = None
else:
    logging.warning("DATABASE_CONNECTION_STRING is missing. Cosmos DB storage will not work.")


# =============================================================================
# THE TEXT ANALYZER FUNCTION
# =============================================================================
@app.route(route="TextAnalyzer")
def TextAnalyzer(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Text Analyzer API was called!")

    # =========================================================================
    # STEP 1: GET THE TEXT INPUT
    # =========================================================================
    text = req.params.get("text")

    if not text:
        try:
            req_body = req.get_json()
            text = req_body.get("text")
        except ValueError:
            pass

    # =========================================================================
    # STEP 2: ANALYZE THE TEXT (if text was provided)
    # =========================================================================
    if text:
        words = text.split()
        word_count = len(words)

        char_count = len(text)
        char_count_no_spaces = len(text.replace(" ", ""))

        sentence_count = len(re.findall(r"[.!?]+", text)) or 1
        paragraph_count = len([p for p in text.split("\n\n") if p.strip()])

        reading_time_minutes = round(word_count / 200, 1)
        avg_word_length = round(char_count_no_spaces / word_count, 1) if word_count > 0 else 0
        longest_word = max(words, key=len) if words else ""

        response_data = {
            "analysis": {
                "wordCount": word_count,
                "characterCount": char_count,
                "characterCountNoSpaces": char_count_no_spaces,
                "sentenceCount": sentence_count,
                "paragraphCount": paragraph_count,
                "averageWordLength": avg_word_length,
                "longestWord": longest_word,
                "readingTimeMinutes": reading_time_minutes
            },
            "metadata": {
                "analyzedAt": datetime.utcnow().isoformat(),
                "textPreview": text[:100] + "..." if len(text) > 100 else text
            }
        }

        # =========================================================================
        # STEP 3.5 - STORE RESULTS IN COSMOS DB
        # =========================================================================
        record_id = str(uuid.uuid4())

        document_to_store = {
            "id": record_id,
            "analysis": response_data["analysis"],
            "metadata": response_data["metadata"],
            "originalText": text
        }

        if cosmos_container is None:
            return func.HttpResponse(
                json.dumps({
                    "error": "Cosmos DB is not configured or connection failed.",
                    "fix": "Check DATABASE_CONNECTION_STRING in local.settings.json and confirm Cosmos DB database/container names.",
                    "analysisResult": response_data
                }, indent=2),
                mimetype="application/json",
                status_code=500
            )

        try:
            cosmos_container.create_item(body=document_to_store)
        except exceptions.CosmosHttpResponseError as e:
            return func.HttpResponse(
                json.dumps({
                    "error": "Failed to store document in Cosmos DB.",
                    "details": str(e),
                    "analysisResult": response_data
                }, indent=2),
                mimetype="application/json",
                status_code=500
            )

        response_data["storedRecordId"] = record_id

        return func.HttpResponse(
            json.dumps(response_data, indent=2),
            mimetype="application/json",
            status_code=200
        )

    # =========================================================================
    # STEP 4: HANDLE MISSING TEXT (Error Response)
    # =========================================================================
    instructions = {
        "error": "No text provided",
        "howToUse": {
            "option1": "Add ?text=YourText to the URL",
            "option2": "Send a POST request with JSON body: {\"text\": \"Your text here\"}",
            "example": "https://your-function-url/api/TextAnalyzer?text=Hello world"
        }
    }

    return func.HttpResponse(
        json.dumps(instructions, indent=2),
        mimetype="application/json",
        status_code=400
    )


# =============================================================================
# ENDPOINT - GetAnalysisHistory
# Route: /api/GetAnalysisHistory
# Method: GET
# =============================================================================
@app.route(route="GetAnalysisHistory", methods=["GET"])
def GetAnalysisHistory(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("GetAnalysisHistory API was called!")

    limit_str = req.params.get("limit")
    try:
        limit = int(limit_str) if limit_str else 10
    except ValueError:
        limit = 10

    if limit < 1:
        limit = 1
    if limit > 100:
        limit = 100

    if cosmos_container is None:
        return func.HttpResponse(
            json.dumps({
                "error": "Cosmos DB is not configured or connection failed.",
                "fix": "Check DATABASE_CONNECTION_STRING in local.settings.json and confirm Cosmos DB database/container names."
            }, indent=2),
            mimetype="application/json",
            status_code=500
        )

    query = f"SELECT TOP {limit} c.id, c.analysis, c.metadata FROM c ORDER BY c._ts DESC"

    try:
        items = list(cosmos_container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))
    except Exception as e:
        return func.HttpResponse(
            json.dumps({
                "error": "Failed to query Cosmos DB.",
                "details": str(e)
            }, indent=2),
            mimetype="application/json",
            status_code=500
        )

    response = {
        "count": len(items),
        "results": items
    }

    return func.HttpResponse(
        json.dumps(response, indent=2),
        mimetype="application/json",
        status_code=200
    )
