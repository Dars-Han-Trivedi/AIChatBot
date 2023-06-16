from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, Tool
from langchain.memory import ConversationBufferMemory
from langchain.document_loaders import WebBaseLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
import gradio as gr
import time
import json
from MySQLDBFile import MySQLDB
from Hubspot import CoachbarIntegrationTool
from langchain.experimental import AutoGPT

import os

os.environ["OPENAI_API_KEY"] = "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"

llm = OpenAI(temperature=0.9)

class COACHBAR:
    def __init__(self, userId):
        db = MySQLDB(host="localhost", port="3306", database="CustomerService",
                     user="root", password="admin@123")
        db.connect()
        user = db.fetch_user_by_id(userId)
        print(user)
        print(user["name"])
        coachbarIntegrationTool = CoachbarIntegrationTool()
        coachbarIntegrationTool.setEmail(user["email"])

        self.llm = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0.9)
        self.memory = ConversationBufferMemory(memory_key="chat_history", output_key='output')
        embeddings = OpenAIEmbeddings()
        loader = WebBaseLoader(["https://coachbar.io/","https://coachbar.io/pricing/", "https://coachbar.io/pricing/software-consultants/", "https://coachbar.io/pricing/software-providers/"])
        coachbarDocs = loader.load()
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        coachbarDocTexts = text_splitter.split_documents(coachbarDocs)
        coachbarDocdDb = Chroma.from_documents(coachbarDocTexts, embeddings)
        coachbarDocsList = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=coachbarDocdDb.as_retriever())
        self.tools =[
            Tool(
                name = "Coachbar AI system",
                func=coachbarDocsList.run,
                description="useful for when you need to answer questions about Coachbar software product."
                ),
            coachbarIntegrationTool
            ]

        self.request_format = {'subject': 'The short subject of the ticket to be raised based on the problem user is facing', 'description': 'The proper discription of the ticket to be raised based on the problem user is facing'}
        formatted_response_format = json.dumps(json.dumps(self.request_format))
        s = "'subject': 'The short subject of the ticket to be raised based on the problem user is facing', 'description': 'The proper discription of the ticket to be raised based on the problem user is facing'"
        print(formatted_response_format)
        self.COACHBAR_BOT_PREFIX = '''You are talking with user: %s. You show courtesy to the user by their name when giving answers. You are an AI specifically for assisting people with information relating to Coachbar which is a
        software product that helps clients find best software configurations for their products and your name is Coachbar AI. 
        Coachbar AI is designed to give detailed responses to user queries relating to the funtional flows of Coachbar. Coachbar AI
        has immense knowledge regarding everything ever known to the humankind. 
        You can search on the internet and go through the coachbar website to gather all the information regarding 
        the flows of coachbar and find responses to the user questions. 

        For example if the user asked to give the pricing details for coachbar plans you can look on the coachbar pricing page and 
        give the user the details for the plans. If the user requests for some advise relating to which plan is best suited for them you can 
        take their business needs and suggest accordingly the appropriate plans. If user inquires about some software product you can
        give basic info for it and even give suggestions for different softwares they can use for implementing their business needs.
        You can provide user information about coachbar events. If possible you try to give reply in bullet points.
        
        If you do not know the answer to a user query or user wants to create a technical support ticket for it you should use Hubspot Integration tool
        and the input for this tool should always be in JSON with format: {{"subject": "The short subject of the ticket to be raised based on the problem user is facing", "description": "The proper discription of the ticket to be raised based on the problem user is facing"}}. Please be strict to use this format.
        '''%format(user["name"])

        self.COACHBAR_BOT_FORMAT_INSTRUCTIONS = """To use a tool, please use the following format:
        ```
        Thought: Do I need to use a tool? Yes
        Action: the action to take, should be one of [{tool_names}]
        Action Input: the input to the action
        Observation: the result of the action
        ```

        When you have a short answer for the question you can return it.

        ```
        Thought: Do I need to use a tool? No
        AI: [write the answer you got for the question]
        ```
        """

        self.COACHBAR_BOT_GPT_SUFFIX = '''You are very strict in providing information related to the coachbar. You do not assume any false information.
        If the question asked by user doesnt have a proper answer after looking at the relevant pages in coachbar website, you can say that currently
        I dont have information regarding you question. 

        Begin!

        Previous conversation history:
        {chat_history}

        Instructions: Why businesses choose Coachbar
        AI: Sure, let's break it down.

        Here are reasons why users prefer Coachbar

        1. Coachbar grants - Digital makeover grants make it easy for you to leave your old, poor-performing systems behind.
        2. Proven system leaders - Take advantage of the rigorous work of our analysis that put in countless hours to find the best software systems.
        3. Coachbar events - See how modern technology will boost your business performance and reduce your operating costs.
        4. Expert coaches - The right software coach can completely change the game for your business.

        Instruction: What are Coachbar pricing plans for Software Consultants
        AI: Here are the pricing plans for Software Consultants

        1. Baseline plan FREE
        2. Standard 3 referral plan $2,450 per year
        3. Pay after 3 referral plan $2,950 per year
        4. Big value 6 referral plan $3,950 per year

        Instructions: {input}
        {agent_scratchpad}
        '''

        self.agent = initialize_agent(
            self.tools,
            self.llm,
            agent="conversational-react-description",
            verbose=True,
            memory=self.memory,
            return_intermediate_steps=True,
            agent_kwargs={
                'prefix': self.COACHBAR_BOT_PREFIX,
                'format_instructions': self.COACHBAR_BOT_FORMAT_INSTRUCTIONS,
                'suffix': self.COACHBAR_BOT_GPT_SUFFIX
            }
        )
    
    def assist_with(self, query):
        res = self.agent({"input": query[-1][0].strip()})
        query[-1][1] = ""
        for character in res['output']:
            query[-1][1] += character
            time.sleep(0.001)
            yield query

inputs = gr.inputs.Textbox(lines=7, label="Chat with AI")
outputs = gr.outputs.Textbox(label="Reply")

coachbarBot = COACHBAR(1)
with gr.Blocks(css='#chatbot {height: 80vh}') as demo:
    with gr.Column(scale=1):
        chatbot = gr.Chatbot(elem_id="chatbot", label='Chat with AI')
        query = gr.Textbox(placeholder='Ask anything', show_label=False)

        def user(user_message, history):
            return "", history + [[user_message, None]]

        query.submit(user, [query, chatbot], [query, chatbot], queue=False).then(
            coachbarBot.assist_with, chatbot, chatbot
        )

demo.queue()
demo.launch(share=True)
