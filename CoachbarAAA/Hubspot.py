import requests
import json

from langchain.callbacks.manager import CallbackManagerForToolRun, AsyncCallbackManagerForToolRun
from langchain.chat_models import ChatOpenAI
from langchain.tools import BaseTool
from typing import Optional


class HubSpotAPI:

    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def create_user(self, email, first_name, last_name, role):
        url = "https://api.hubapi.com/crm/v3/owners"

        user_data = {
            "email": email,
            "firstName": first_name,
            "lastName": last_name,
            "role": role
        }

        payload = json.dumps(user_data)

        response = requests.post(url, headers=self.headers, data=payload)

        if response.status_code == 201:
            print("User created successfully.")
        else:
            print(f"Failed to create user. Status code: {response.status_code}")
            print(response.text)

    def create_ticket(self, subject, content, contact_email):
        url = "https://api.hubapi.com/crm/v3/objects/tickets"

        ticket_data = {
            "properties": {
                "subject": subject,
                "content": content,
                "hs_pipeline_stage": 1
            },
            "associations": [{
                "to": {
                    "id": "",
                }
            }]
        }

        if contact_email:
            contact_id = self.get_contact_id(contact_email)
            if contact_id:
                ticket_data["associations"][0]["to"]["id"] = contact_id

        payload = json.dumps(ticket_data)

        response = requests.post(url, headers=self.headers, data=payload)

        if response.status_code == 201:
            print("Ticket created successfully.")
            return response

        else:
            print(f"Failed to create ticket. Status code: {response.status_code}")
            print(response.text)

    def get_contact_id(self, email):
        url = f"https://api.hubapi.com/contacts/v1/contact/email/{email}/profile"

        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            data = response.json()
            return data["vid"] if "vid" in data else None
        else:
            print(f"Failed to retrieve contact. Status code: {response.status_code}")
            print(response.text)



class CoachbarIntegrationTool(BaseTool):
    name = 'Hubspot Integration'
    description = 'Hubspot integration with coachbar. Useful for calling hubspot api to create ticket for user query. '
    return_direct = True
    #llm = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0.9)
    email = ""
    hubSpotAPI = HubSpotAPI("pat-na1-7a36c840-bf45-4866-952d-e77789cee74f")

    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Use the tool."""
        ticket = json.loads(query)
        response = self.hubSpotAPI.create_ticket(ticket["subject"], ticket["description"], self.email)
        print(response)
        id = json.loads(response.text)["id"]
        return "Your ticket is created with ID : " + id
        #return "Yes I will use Hubspot tool : " + query

    async def _arun(self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("custom_search does not support async")

    def setEmail(self, email):
        self.email = email
