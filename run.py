from http.client import HTTPException

from dotenv import load_dotenv

from flask import Flask, jsonify, redirect, request
from flask_cors import CORS
from apispec import APISpec
from flask_swagger_ui import get_swaggerui_blueprint
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin

from ask_viridium_ai.routes import MainRoutes
from ask_viridium_ai.tracking import AppInsightsConnector

from global_constants import GlobalConstants

global_constants = GlobalConstants

load_dotenv()

app = Flask(__name__)
CORS(app)

logger = AppInsightsConnector().get_logger()

main_routes = MainRoutes()
app.register_blueprint(main_routes.blueprint, url_prefix=GlobalConstants.api_version)

swagger_endpoint = global_constants.swagger_endpoint

# Swagger and APISpec setup
spec = APISpec(
    title=global_constants.apispec_config.title,
    version=global_constants.apispec_config.version,
    openapi_version=global_constants.apispec_config.openapi_version,
    plugins=[FlaskPlugin(), MarshmallowPlugin()],
)

with app.test_request_context():
    for view in [
        main_routes.home,
        main_routes.ask_viridium_ai,
        main_routes.health_check,
    ]:
        spec.path(view=view)

swaggerui_blueprint = get_swaggerui_blueprint(
    swagger_endpoint,
    global_constants.api_swagger_json,
    config={"app_name": global_constants.swagger_app_name},
)

app.register_blueprint(swaggerui_blueprint, url_prefix=swagger_endpoint)


@app.route('/')
def root():
    return redirect(global_constants.api_version)


@app.route(global_constants.api_swagger_json)
def create_swagger_spec():
    return jsonify(spec.to_dict())


@app.before_request
def log_request_info():
    logger.info(f"API REQUEST : {request.method} {request.path} - Headers: {dict(request.headers)} - Body: {request.get_data()}")


@app.after_request
def log_response_info(response):
    logger.info(f"API RESPONSE : {response.status} - Headers: {dict(response.headers)}")
    return response


@app.errorhandler(Exception)
def handle_exception(e):
    # Pass through HTTP errors
    if isinstance(e, HTTPException):
        logger.error(f"HTTP Exception: {e}")
        return jsonify(error=str(e)), e.code
    else:
        # Handle non-HTTP exceptions only
        logger.exception("Unhandled Exception: %s", e)
        return jsonify(error="An unexpected error occurred. Please try again later."), 500


if __name__ == '__main__':
    app.run(debug=True)
