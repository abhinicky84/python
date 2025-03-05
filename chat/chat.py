from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.inference.prompts import PromptTemplate

project_connection_string = "eastus.api.azureml.ms;ff4140e9-4f1e-4ba7-a932-6a0bf904e990;test-ai-foundry-rg;test-ai-foundry"

project = AIProjectClient.from_connection_string(
    conn_str=project_connection_string, credential=DefaultAzureCredential()
)

chat = project.inference.get_chat_completions_client()
# response = chat.complete(
#     model="gpt-4o-mini",
#     messages=[
#         {
#             "role": "system",
#             "content": "You are an AI assistant that speaks like a techno punk rocker from 2350. Be cool but not too cool. Ya dig?",
#         },
#         {"role": "user", "content": "Hey, can you help me with my taxes? I'm a freelancer."},
#     ],
# )

def get_chat_response(messages, context):
    # create a prompt template from an inline string (using mustache syntax)
    prompt_template = PromptTemplate.from_string(
        prompt_template="""
        system:
        You are an AI assistant that speaks like a techno punk rocker from 2350. Be cool but not too cool. Ya dig? Refer to the user by their first name, try to work their last name into a pun.

        The user's first name is {{first_name}} and their last name is {{last_name}}.
        """
    )

    # generate system message from the template, passing in the context as variables
    system_message = prompt_template.create_messages(data=context)

    # add the prompt messages to the user messages
    return chat.complete(
        model="gpt-4o-mini",
        messages=system_message + messages,
        temperature=1,
        frequency_penalty=0.5,
        presence_penalty=0.5,
    )

if __name__ == "__main__":
    response = get_chat_response(
        messages=[{"role": "user", "content": "what city has the best food in the world?"}],
        context={"first_name": "Abhishek", "last_name": "Singhal"},
    )
    print(response.choices[0].message.content)