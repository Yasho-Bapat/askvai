"""
AskViridium class is used to handle the query and get results.

Usage:
    from ask_viridium_ai import AskViridium

    ask_vai = AskViridium()  # Initialize the AskViridium class
    ans = ask_vai.query("Nitrogen, Cryogenic Liquid", "Matheson Tri-Gas, Inc.",
                        "Heat Treatment, Hipping, Annealing and Tempering")  # Query the system with specific parameters

logs are stored in AppInsights and data.json
"""

import json
import time
from dotenv import load_dotenv
from typing import Optional

from langchain.prompts import ChatPromptTemplate
from langchain_core.utils.function_calling import convert_to_openai_function
from langchain_openai import AzureChatOpenAI
from openai import BadRequestError
from langchain_core.output_parsers.openai_functions import JsonOutputFunctionsParser
from langchain_community.callbacks import get_openai_callback
import logging

from global_constants import GlobalConstants  # Global constants used in the script
from models import MaterialComposition, MaterialInfo  # Models for chemical composition and material information
from .tracking import AppInsightsConnector  # Logger for tracking and logging information

load_dotenv()


class AskViridium:
    def __init__(self):
        """Initialize the AskViridium class."""
        self.logger = AppInsightsConnector().get_logger()  # Initialize the logger
        self.loginfo = dict()  # Dictionary to store log information
        self.constants = GlobalConstants()  # Initialize global constants
        self.model_name = self.constants.model_name  # Model name from constants
        self.deployment_name = self.constants.deployment_name  # Deployment name from constants

        self.llm = AzureChatOpenAI(
            deployment_name=self.deployment_name,
            temperature=0,
            max_tokens=800,
            n=3
        )

        # Initialize prompts and functions
        self.cheminfo_prompt = self.prompt1_init()  # Prompt for chemical information
        self.analysis_prompt = self.prompt2_init()  # Prompt for analysis
        self.cheminfo_function, self.analysis_function = self.openai_functions_creation()  # Create OpenAI functions
        self.cheminfo_model, self.analysis_model = self.bind_function()  # Bind functions to models
        self.parser = JsonOutputFunctionsParser()  # Initialize JSON output parser
        self.cheminfo_chain = self.cheminfo_prompt | self.cheminfo_model | self.parser  # Chain for chemical info
        self.analysis_chain = self.analysis_prompt | self.analysis_model | self.parser  # Chain for analysis
        self.chemical_composition = None  # Placeholder for chemical composition
        self.pfas = None  # Placeholder for PFAS status

        self.result = str()  # Placeholder for the result

    def prompt1_init(self):
        """
        Initialize the prompt for chemical information.

        Returns:
            ChatPromptTemplate: The prompt template for finding chemical composition of the material provided.
        """
        with open('ask_viridium_ai/system_prompt_templates/findchemicals_prompt.txt', 'r') as file:
            cheminfo_system_prompt = file.read()

        prompt = ChatPromptTemplate.from_messages([
            ("system", cheminfo_system_prompt),
            ("human", "Material Name: {material}"),
        ])
        return prompt

    def prompt2_init(self):
        """
        Initialize the prompt for analysis.

        Returns:
            ChatPromptTemplate: The prompt template for analysis.
        """
        with open('ask_viridium_ai/system_prompt_templates/new_prompt.txt', 'r') as file:
            analysis_system_prompt = file.read()

        prompt = ChatPromptTemplate.from_messages([
            ("system", analysis_system_prompt),
            ("human",
             "Material Name: {material}, manufactured by {manufacturer}. CONTEXT: used as {usecase}. Its chemical composition is: {chemical_composition}. Additional info: {additional_info}")
        ])
        return prompt

    def openai_functions_creation(self):
        """
        Create OpenAI functions for chemical composition and analysis by converting Pydantic objects.

        Returns:
            list: A list containing the chemical info function and analysis function.
        """
        cheminfo_function = [convert_to_openai_function(MaterialComposition)]

        analysis_function = [convert_to_openai_function(MaterialInfo)]
        return [cheminfo_function, analysis_function]

    def bind_function(self):
        """
        Bind functions to the LLM for function calling.

        Returns:
            list: a list of models of material composition and of performing the PFAS analysis
        """
        cheminfo_model = self.llm.bind_functions(
            functions=self.cheminfo_function,
            function_call={"name": "MaterialComposition"}
        )
        # Bind the analysis function to the LLM
        analysis_model = self.llm.bind_functions(
            functions=self.analysis_function,
            function_call={"name": "MaterialInfo"}
        )
        return [cheminfo_model, analysis_model]

    def query(self, material_name, manufacturer_name: Optional[str] = "Not Available",
              work_content: Optional[str] = "Not Available"):
        """
        Handle the query and get results.

        Args:
            material_name (str): The name of the material.
            manufacturer_name (Optional[str]): The name of the manufacturer. Defaults to "Not Available".
            work_content (Optional[str]): The use case or context. Defaults to "Not Available".

        Returns:
            str: The result of the analysis.
        """
        start = time.perf_counter()

        self.logger.info("Received query: Material=%s, Manufacturer=%s, Work Content=%s",
                         material_name, manufacturer_name, work_content)
        material = material_name
        manufacturer = manufacturer_name
        work_content = work_content

        try:
            with get_openai_callback() as cb:
                # Invoke the chemical info chain and get the chemical composition
                self.logger.info("Invoking chemical information chain")
                self.chemical_composition = self.cheminfo_chain.invoke(
                    {"material": material, "example": self.constants.chemical_composition_example})
                self.logger.info("Chemical composition received: %s", self.chemical_composition)
                chemicals_list = [chemical["name"] for chemical in self.chemical_composition["chemicals"]]
                tokens_for_cheminfo = cb.total_tokens
                cost_for_cheminfo = cb.total_cost
        except BadRequestError as e:
            self.logger.error("OpenAI BadRequestError during chemical composition retrieval: %s", e)
            self.chemical_composition = None
            chemicals_list = list()
            tokens_for_cheminfo = 0
            cost_for_cheminfo = 0
        except Exception as e:
            self.logger.exception("Unexpected error during chemical composition retrieval: %s", e)
            self.chemical_composition = None
            chemicals_list = list()
            tokens_for_cheminfo = 0
            cost_for_cheminfo = 0

        try:
            with get_openai_callback() as cb:
                # Invoke the analysis chain and get the analysis result
                self.logger.info("Invoking analysis chain")
                self.result = self.analysis_chain.invoke(
                    {"material": material, "manufacturer": manufacturer, "usecase": work_content,
                     "chemical_composition": chemicals_list, "example": self.constants.analysis_example,
                     "additional_info": None})
                self.logger.info("Analysis result received: %s", self.result)
                tokens_for_analysis = cb.total_tokens
                cost_for_analysis = cb.total_cost
                self.pfas = self.result["decision"]
        except BadRequestError as e:
            self.logger.error("OpenAI BadRequestError during analysis: %s", e)
            self.pfas = None
            tokens_for_analysis = 0
            cost_for_analysis = 0
        except Exception as e:
            self.logger.exception("Unexpected error during analysis: %s", e)
            self.pfas = None
            tokens_for_analysis = 0
            cost_for_analysis = 0

        self.loginfo = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            "duration": time.perf_counter() - start,
            "material": material_name,
            "manufacturer": manufacturer_name,
            "tokens_used_for_chemical_composition": tokens_for_cheminfo,
            "tokens_used_for_analysis": tokens_for_analysis,
            "cost_chemical_composition": cost_for_cheminfo,
            "cost_analysis": cost_for_analysis,
            "total_cost": cost_for_cheminfo + cost_for_analysis,
            "chemical_composition": self.chemical_composition,
            "PFAS_status": self.pfas,
            "result": self.result
        }

        self.store()  # Store the result in data.json

        return self.result

    def handle_user_query(self, additional_info, material, manufacturer, work_content, chemicals_list):
        """
        Handle user query with additional information.

        Args:
            additional_info (str): Additional information provided by the user.
            material (str): The name of the material.
            manufacturer (str): The name of the manufacturer.
            work_content (str): The use case or context.
            chemicals_list (list): List of chemicals.
        """
        try:
            with get_openai_callback() as cb:
                self.logger.info("Handling user query with additional info")
                self.result = self.analysis_chain.invoke(
                    {"material": material, "manufacturer": manufacturer, "usecase": work_content,
                     "chemical_composition": chemicals_list, "example": self.constants.analysis_example,
                     "additional_info": additional_info})
                self.logger.info("Result of user query with additional info: %s", self.result)
        except Exception as e:
            self.logger.exception("Unexpected error during user query handling: %s", e)

    def store(self):
        """
        Store the result in a JSON file.

        Returns:
            str: Confirmation message indicating that the results are saved.
        """
        try:
            with open("data_dump/data.json", 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            self.logger.warning("data.json not found, creating a new one")
            data = []

        try:
            data.append(self.loginfo)

            with open("data_dump/data.json", 'w') as file:
                json.dump(data, file, indent=4)

            self.logger.info("Results stored in data.json")
            return True
        except Exception as e:
            self.logger.exception("Data could not be stored due to the following exception: %s", e)
            return False


if __name__ == '__main__':
    ask_vai = AskViridium()
    ans = ask_vai.query("Nitrogen, Cryogenic Liquid", "Matheson Tri-Gas, Inc.",
                        "Heat Treatment, Hipping, Annealing and Tempering")  # Query the system with specific parameters
