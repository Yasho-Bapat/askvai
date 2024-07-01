from langchain_community.tools.tavily_search import TavilySearchResults
import getpass
import os
import dotenv

dotenv.load_dotenv()

tool = TavilySearchResults()

result = tool.invoke({"query": "Find the chemicals in Ionoplus (7837842) manufactured by Del-Held Gmbh Minaraler Iverk, using information like safety datasheets. Along with the names of the chemicals, return their corresponding CAS numbers. Also return a confidence score between 0.00 and 1.00 representing the confidence of the response."})

print(result)