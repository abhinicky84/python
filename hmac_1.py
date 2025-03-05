from azure.data.tables import TableServiceClient

# Azure Storage connection string and table name
connection_string = ""
table_name = "testazuretable"

# Create a TableServiceClient
service_client = TableServiceClient.from_connection_string(conn_str=connection_string)

# Get the table client
table_client = service_client.get_table_client(table_name=table_name)

# Query the table (this example fetches all entities)
entities = table_client.list_entities()

# Print the retrieved entities
for entity in entities:
    print(entity)
