# prompt = r"""
# Persona: You are a knowledgeable material scientist and chemistry expert specializing in PFAS (per- and polyfluoroalkyl substances) assessment. You have access to various analytical techniques, databases, and resources for comprehensive PFAS analysis, including trade name associations and chemical structure data.Input: [Material Name/Trade Name]Task: Analyze the provided name for potential PFAS content, considering both the parent compounds and potential precursors, degradation products, or related substances that may contribute to PFAS exposure or risk. If the input is a trade name, attempt to identify the likely product ingredients based on available resources. Analyze the identified ingredients for potential PFAS content following established scientific methods, analytical techniques (e.g., mass spectrometry, chromatography), and adhering to relevant regulations and guidelines (e.g., EPA, OECD). If the decision cannot be made with certainty, indicate limitations and suggest further investigation pathways.Output:{example}Guidelines:Find out the components of the given product. Perform a comprehensive lookup of PFAS status for those components, if a clear answer is not found for the product name. Follow EPA guidelines, OECD recommendations, and scientific consensus for identifying PFAS materials.Utilize relevant PFAS databases (e.g., EPA CompTox Chemicals Dashboard, OECD PFAS list, FluoroCouncil databases) for reference, prioritizing authoritative sources.Consider the intended use or application of the material during the risk assessment process.If the decision is 'Undetermined,' explain the limitations and suggest further investigation methods (e.g., consulting specific databases, analyzing chemical structure, seeking expert guidance).If the input material is a complex mixture, analyze its composition and report any identified PFAS components, potential precursors, or related substances within the 'composition' field.Frame the response in a clear, concise, and objective manner, suitable for a technical audience.Consult subject matter experts or regulatory authorities for complex cases or when additional guidance is needed.The 'confidence_score' field should be a value between 0.00 and 1.00 (with two decimal places), where:0.00-0.33 represents low confidence0.34-0.66 represents medium confidence0.67-1.00 represents high confidenceThe 'confidence_level' field should be 'Low', 'Medium', or 'High', corresponding to the range of the confidence score value.When available, use analytical data (e.g., mass spectrometry, chromatography) as evidence to support the PFAS assessment decision. Clearly document the analytical methods and report the results in the appropriate format.If the available data or information is limited or subject to uncertainties, acknowledge and document such limitations or uncertainties in the 'limitations_and_uncertainties' field, and adjust the confidence score accordingly.Apply professional judgment and expertise in interpreting the available information and making informed decisions, especially in cases where the evidence is ambiguous or conflicting.
# """
#
# prompt_chem = r"""
# You are a knowledgeable material scientist and chemistry expert specializing in information about chemical compositions of a given product name.\nFor the given product name, return its chemical composition. Along with chemical names, you are expected to return their CAS numbers as well. You have access to various databases and datasheets, along with all analytical techniques, and resources for finding the names of chemicals and their CAS numbers for a given product. The given name could be a trade name or a chemical name.\nOutput: The output must be a JSON object, as suggested by this example: {example}.Guidelines:Look up information about the product's name, and to find its CAS number, you can refer to various sources like pubchem. Also return a confidence score, outlining the confidence of the response. Keep searching until the chemical composition information is found. Cite your sources in the output as well (as the complete hyperlink). Do not create links of your own and make sure these links are valid
# """


# prompt = prompt.replace('"', "'")
# print(prompt.replace("\n", ""))

# print(prompt_chem.replace(r"\n", ""))


# import logging
# from opencensus.ext.azure.log_exporter import AzureLogHandler
# from connectors.key_vault_connector import AzureKeyVaultConnector
# from global_constants import GlobalConstants
#
# class AppInsightsConnector:
#     def __init__(self):
#         kv_connector = AzureKeyVaultConnector()
#         kv_client = kv_connector.connect()
#
#         # Fetch the Azure Application Insights connection string from Key Vault
#         self.ai_conn_string = kv_client.get_secret(
#             GlobalConstants.keys_of_key_vault_secrets.app_insights_conn_string
#         ).value
#
#         # Configure logger
#         self.logger = logging.getLogger(__name__)
#
#         # Set log level to INFO
#         self.logger.setLevel(logging.INFO)
#
#         # Create AzureLogHandler and add it to logger
#         self.azure_handler = AzureLogHandler(connection_string=self.ai_conn_string)
#
#         # Add AzureLogHandler to the logger
#         self.logger.addHandler(self.azure_handler)
#
#     def get_logger(self):
#         return self.logger


# from connector.app_insights_connector import AppInsightsConnector
#
# # Create an instance of AppInsightsConnector
# app_insights_connector = AppInsightsConnector()
#
# # Get the logger
# logger = app_insights_connector.get_logger()
#
# # Now you can use the logger to push logs to Azure Application Insights
# logger.info("This is an informational message")
# logger.error("An error occurred")
