from dotenv import load_dotenv
import os
from models import PolicySummary
import getpass
import os
from langchain_google_genai import ChatGoogleGenerativeAI


load_dotenv()
if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter your Google AI API key: ")
    

