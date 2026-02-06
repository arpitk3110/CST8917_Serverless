# Database Choice 

Azure Cosmos DB.

## Justification
Azure Cosmos DB is the most suitable database for this lab because the Text Analyzer function produces JSON output, and Cosmos DB is designed to store and manage JSON documents natively. The serverless tier aligns well with serverless application principles by automatically scaling and charging only for usage.It does not require predefined schemas, which simplifies development and reduces configuration effort. Additionally, Cosmos DB integrates very well with Azure Functions using the Python SDK, making it reliable and easy to use for this lab.

## Alternatives Considered
Azure SQL Database was considered but rejected because it requires defining schemas and tables, which adds unnecessary complexity for storing flexible JSON data. Azure Table Storage was also evaluated, but it has limited querying capabilities and is less flexible when working with complex JSON documents. Azure Blob Storage was not selected because it is not intended to function as a database and does not support efficient querying of stored analysis results.

## Cost Considerations
Azure Cosmos DB offers a free tier and a serverless pricing model, which makes it well-suited for a student Azure account. With serverless pricing, costs are incurred only when requests are made, and the expected usage for this lab stays within free or very low-cost limits. This minimizes the risk of unexpected charges while still providing a fully managed and scalable database solution.
