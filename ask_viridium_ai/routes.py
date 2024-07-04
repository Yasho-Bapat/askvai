from flask import Blueprint, jsonify, render_template, request
from werkzeug.exceptions import HTTPException

from global_constants import GlobalConstants
from .ask_viridium_ai import AskViridium
from .constants import AskViridiumConstants
from .tracking import AppInsightsConnector

logger = AppInsightsConnector().get_logger()


class MainRoutes:
    """
    This class defines the routes for Ask Viridium AI Service.
    """

    def __init__(self):
        """
        Initializes the blueprint for route definitions.
        """
        self.blueprint = Blueprint("main_routes", __name__, template_folder="templates", static_folder="static")

        # Reference to global and module-specific constants
        self.global_constants = GlobalConstants
        self.constants = AskViridiumConstants

        # Define route for home page
        self.blueprint.add_url_rule(
            "/",
            view_func=self.home,
            methods=[self.global_constants.rest_api_methods.get_api],
        )

        # Define route for AI request
        self.blueprint.add_url_rule(
            "/ask-viridium-ai",
            view_func=self.ask_viridium_ai,
            methods=[self.global_constants.rest_api_methods.post],
        )

        # Define route for health check
        self.blueprint.add_url_rule("/health", view_func=self.health_check)

    def return_api_response(self, status, message, result=None, additional_data=None):
        """
        Constructs and returns a JSON response.

        Args:
            status (int): The status code of the response.
            message (str): The message of the response.
            result (Any, optional): The result of the response. Defaults to None.
            additional_data (dict, optional): Additional data to include in the response. Defaults to None.

        Returns:
            tuple: A tuple containing the JSON response and the status code.
        """
        response_data = {
            self.global_constants.api_response_parameters.status: status,
            self.global_constants.api_response_parameters.message: message,
            self.global_constants.api_response_parameters.result: result,
        }
        if additional_data:
            response_data.update(additional_data)

        logger.info(f"Returning API response: {response_data}")
        return jsonify(response_data), status

    def validate_request_data(self, request_data, required_params):
        """
        Validates that all required parameters are present in the request data.

        Args:
            request_data (dict): The request data to validate.
            required_params (list): The list of required parameters.

        Returns:
            tuple: A tuple containing a boolean indicating if the validation was successful and a list of missing parameters if applicable.
        """
        missing_params = [param for param in required_params if param not in request_data]
        if missing_params:
            logger.warning(f"Validation failed. Missing parameters: {missing_params}")
            return False, missing_params
        return True, None

    def home(self):
        """
        Renders the home page.

        Returns:
            flask.Response: The rendered home page.
        """
        logger.info("Rendering home page")
        return render_template("index.html")

    def ask_viridium_ai(self):
        """
        Handles AI query requests.

        Returns:
            flask.Response: The API response.
        """
        try:
            request_data = request.get_json()

            required_params = [self.constants.input_parameters["material_name"]]

            valid_request, missing_params = self.validate_request_data(request_data, required_params)
            if not valid_request:
                return self.return_api_response(
                    self.global_constants.api_status_codes.bad_request,
                    self.global_constants.api_response_messages.missing_required_parameters,
                    f"{self.global_constants.api_response_parameters.missing_parameters}: {missing_params}",
                )

            ask_vai = AskViridium()
            ask_vai.query(
                request_data[self.constants.input_parameters["material_name"]],
                request_data.get(self.constants.input_parameters["manufacturer_name"]),
                request_data.get(self.constants.input_parameters["work_content"])
            )

            return self.return_api_response(
                self.global_constants.api_status_codes.ok,
                self.global_constants.api_response_messages.success,
                ask_vai.result,
            )
        except HTTPException as e:
            logger.error(f"HTTP exception: {e}")
            return self.return_api_response(e.code, str(e))
        except Exception as e:
            logger.exception("Unhandled exception occurred")
            return self.return_api_response(
                self.global_constants.api_status_codes.internal_server_error,
                "An unexpected error occurred. Please try again later."
            )

    def health_check(self):
        """
        Returns a simple health check response.

        Returns:
            tuple: A tuple containing the JSON response and the status code.
        """
        logger.info("Health check endpoint called")
        return self.return_api_response(
            self.global_constants.api_status_codes.ok,
            self.global_constants.api_response_messages.server_is_running,
        )
