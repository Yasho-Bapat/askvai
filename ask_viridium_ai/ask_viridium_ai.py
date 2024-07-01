import dotenv
import json
from typing import Optional, List
import time

from langchain.prompts import ChatPromptTemplate
from langchain_core.utils.function_calling import convert_to_openai_function
from langchain_openai import AzureChatOpenAI
from langchain_core.output_parsers.openai_functions import JsonOutputFunctionsParser
from langchain_community.callbacks import get_openai_callback

from global_constants import GlobalConstants  # Global constants used in the script
from models import MaterialComposition, MaterialInfo  # Models for chemical composition and material information
from .tracking import Logger  # Logger for tracking and logging information


dotenv.load_dotenv()  # Load environment variables from a .env file


class AskViridium:
    def __init__(self):
        """Initialize the AskViridium class."""
        self.logger = Logger()  # Initialize the logger
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
        with open('ask_viridium_ai/findchemicals_prompt.txt', 'r') as file:
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
        with open('ask_viridium_ai/new_prompt.txt', 'r') as file:
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

    def log(self, time, material_name, manufacturer_name, tokens_for_cheminfo, tokens_for_analysis, cost_cheminfo, cost_analysis, chemlist):
        """
        Log information about the query and results.

        Args:
            time (float): The current time.
            material_name (str): The name of the material.
            manufacturer_name (str): The name of the manufacturer.
            tokens_for_cheminfo (int): Tokens used for chemical information.
            tokens_for_analysis (int): Tokens used for analysis.
            cost_cheminfo (float): Cost for chemical information.
            cost_analysis (float): Cost for analysis.
            chemlist (list): List of chemicals.
        """
        self.loginfo["time"] = time
        self.loginfo["material_name"] = material_name
        self.loginfo["manufacturer_name"] = manufacturer_name
        self.loginfo["tokens_used_for_chemical_composition"] = tokens_for_cheminfo
        self.loginfo["cost_chemical_composition"] = cost_cheminfo
        self.loginfo["tokens_used_for_analysis"] = tokens_for_analysis
        self.loginfo["cost_analysis"] = cost_analysis
        self.loginfo["total_cost"] = cost_analysis + cost_cheminfo
        self.loginfo["chemical_composition"] = str(chemlist)
        self.loginfo["PFAS_status"] = self.pfas
        self.loginfo["user_id"] = "umesh"  # placeholder

        self.logger.log(info=self.loginfo)  # Log the information

    def query(self, material_name, manufacturer_name: Optional[str] = "Not Available", work_content: Optional[str] = "Not Available", additional_info: Optional[str] = None):
        """
        Handle the query and get results.

        Args:
            material_name (str): The name of the material.
            manufacturer_name (Optional[str]): The name of the manufacturer. Defaults to "Not Available".
            work_content (Optional[str]): The use case or context. Defaults to "Not Available".
            additional_info (Optional[str]): Additional information. Defaults to None.

        Returns:
            str: The result of the analysis.
        """
        material = material_name
        manufacturer = manufacturer_name
        work_content = work_content
        rn = time.time()  # Current time for logging

        with get_openai_callback() as cb:
            # Invoke the chemical info chain and get the chemical composition
            self.chemical_composition = self.cheminfo_chain.invoke(
                {"material": material, "example": self.constants.chemical_composition_example})
            print(self.chemical_composition["chemicals"])
            chemicals_list = [chemical["name"] for chemical in self.chemical_composition["chemicals"]]
            tokens_for_cheminfo = cb.total_tokens
            cost_for_cheminfo = cb.total_cost

        with get_openai_callback() as cb:
            # Invoke the analysis chain and get the analysis result
            self.result = self.analysis_chain.invoke(
                {"material": material, "manufacturer": manufacturer, "usecase": work_content,
                 "chemical_composition": chemicals_list, "example": self.constants.analysis_example,
                 "additional_info": None})
            tokens_for_analysis = cb.total_tokens
            cost_for_analysis = cb.total_cost
            self.pfas = self.result["decision"]

        # Log the query and results
        self.log(rn, material_name, manufacturer_name, tokens_for_cheminfo, tokens_for_analysis, cost_for_cheminfo, cost_for_analysis, chemicals_list)
        self.logger.save()  # Save the log

        store = self.store()  # Store the result
        print(store)

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
        with get_openai_callback() as cb:
            self.result = self.analysis_chain.invoke(
                {"material": material, "manufacturer": manufacturer, "usecase": work_content,
                 "chemical_composition": chemicals_list, "example": self.constants.analysis_example,
                 "additional_info": additional_info})

    def store(self):
        """
        Store the result in a JSON file.

        Returns:
            str: Confirmation message indicating that the results are saved.
        """
        # Read existing data from the file
        try:
            with open("data.json", 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            data = []

        # Append the new result
        data.append(self.result)

        # Write the updated data back to the file
        with open("data.json", 'w') as file:
            json.dump(data, file, indent=4)

        return "results saved"  # Return a confirmation message


if __name__ == '__main__':
    ask_vai = AskViridium()  # Initialize the AskViridium class
    ans = ask_vai.query("Nitrogen, Cryogenic Liquid", "Matheson Tri-Gas, Inc.",
                        "Heat Treatment, Hipping, Annealing and Tempering")  # Query the system with specific parameters
