####################################################################################################
# Project Name: Motive Event Management System
# Course: COMP70025 - Software Systems Engineering
# File: eventManager.py
# Description: Defines CRUD functionality for events.
#
# Authors: James Hartley, Ankur Desai, Patrick Borman, Julius Gasson, and Vadim Dunaevskiy
# Date: 2024-02-20
# Version: 1.1
#
# Changes: Fixed behaviour of functions against unit tests.
#
# Notes: Currently, all functions rely on the unique event_id assigned by Supabase to pull
#        information, which may not be ideal for the front end. Also need to complete the api
#        routes at the end of this file to be deployed.
####################################################################################################


from flask import Flask, jsonify
from supabase import create_client, Client
from dotenv import load_dotenv
import os
import functions_framework

app = Flask(__name__)

# Create a Supabase client
load_dotenv()
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# Schema for request validation
object_types = ["venue", "artist", "attendee", "event", "ticket"]
account_types = [ot for ot in object_types if ot not in ["event", "ticket"]]
non_account_types = [ot for ot in object_types if ot not in account_types]
attributes_schema = {
    "venue": [
        "user_id",
        "venue_name",
        "email",
        "street_address",
        "city",
        "postcode",
        "bio",
    ],
    "artist": [
        "user_id",
        "artist_name",
        "email",
        "street_address",
        "city",
        "postcode",
        "genres",
        "spotify_artist_id",
        "bio",
    ],
    "attendee": [
        "user_id",
        "first_name",
        "last_name",
        "email",
        "street_address",
        "city",
        "postcode",
        "bio",
    ],
    "event": [
        "event_id",
        "venue_id",
        "event_name",
        "date_time",
        "total_tickets",
        "sold_tickets",
        "artist_ids",
    ],
    "ticket": ["ticket_id", "event_id", "attendee_id", "price", "status"],
}
# Attribute keys are paired with boolean values for get requests, or the value to be added to the
# database otherwise.
request_template = ["function", "object_type", "identifier", "attributes"]


def create_event(request):
    """
    Inserts an event into the Supabase 'events' table.

    Args:
        request: A dictionary containing 'object_type', 'identifier', and 'attributes'.

    Returns:
        tuple: (str, dict or str) indicating success (an event_id is returned) and either a success
            or error message.
    """
    attributes = request["attributes"]
    data_to_insert = {key: value for key, value in attributes.items()}

    try:
        result, error = supabase.table("events").insert(data_to_insert).execute()

        result_key, result_value = result
        error_key, error_value = error

        # Check the content of the 'result' tuple
        if result_key == "data" and result_value:
            event_id = result_value[0].get("event_id")
            return event_id, "Event creation was successful."
        elif error_value:
            return None, f"An error occurred: {error_value}"
        else:
            return None, "Unexpected response: No data returned after insert."
    except Exception as e:
        return None, f"An exception occurred: {str(e)}"


def update_event(request):
    """
    Updates an event in the 'events' table in the Supabase database.

    Args:
        request: A dictionary containing 'object_type', 'identifier', and 'attributes'.

    Returns:
        A tuple containing a boolean indicating success and a message or data.
    """
    object_type = request["object_type"]
    identifier = request["identifier"]  # Here this must be event_id
    attributes = request["attributes"]
    data_to_update = {
        key: value for key, value in attributes.items() if value is not None
    }

    if not data_to_update:
        return False, "No valid attributes provided for update."

    try:
        query = (
            supabase.table(object_type + "s")
            .update(data_to_update)
            .eq("event_id", identifier)
        )
        result, error = query.execute()

        result_key, result_value = result
        error_key, error_value = error

        # Check the content of the 'result' tuple
        if result_key == "data" and result_value:
            # Check if any attributes have been updated
            updated_attributes = result_value[0]
            for key, value in attributes.items():
                if key in updated_attributes and updated_attributes[key] != value:
                    return False, f"Failed to update {key} attribute."
            return True, "Event updated successfully."
        elif error_value:
            return False, f"An error occurred: {error_value}"
        else:
            return False, "Unexpected response: No data returned after update."
    except Exception as e:
        return False, f"An exception occurred: {str(e)}"


def delete_event(request):
    """
    Deletes an event from the 'events' table in the Supabase database.

    Args:
        request: A dictionary containing 'object_type', 'identifier'.

    Returns:
        A tuple containing a boolean indicating success and a message.
    """
    object_type = request["object_type"]
    identifier = request["identifier"]  # Here this must be event_id

    try:
        # Delete the record from the specified table
        result = (
            supabase.table(object_type + "s")
            .delete()
            .eq("event_id", identifier)
            .execute()
        )

        # Assuming result.data contains the number of deleted rows
        if result.data:
            return True, "Event deletion was successful."
        else:
            return False, "Event not found or already deleted."
    except Exception as e:
        return False, f"An exception occurred: {str(e)}"


def get_event_info(request):
    """
    Retrieves specific information for an event from the 'events' table in the Supabase database
    based on a request structure that includes an event ID and attributes marked as True for retrieval.

    Args:
        request (dict): A dictionary containing 'object_type', 'identifier', and 'attributes' where
                        'attributes' is a dict with keys as attribute names and boolean values indicating
                        whether to retrieve them.

    Returns:
        A tuple containing a boolean indicating success, and either the event data for the specified
        attributes or an error message.
    """
    event_id = request["identifier"]
    object_type = request["object_type"]

    attributes_to_fetch = [
        attr for attr, include in request.get("attributes", {}).items() if include
    ]

    try:
        data = (
            supabase.table(object_type + "s")
            .select(", ".join(attributes_to_fetch))
            .eq("event_id", event_id)
            .execute()
        )
        if data.data:
            return True, {
                "message": "Event found",
                "data": data.data[0],
            }
        else:
            return False, {"message": "Event not found", "data": []}
    except Exception as e:
        return False, {"message": f"An API error occurred: {str(e)}", "data": []}


def get_events_for_venue(request):
    """
    Queries all events for a given venue from the 'events' table in the Supabase database using a request
        JSON structure.

    Args:
        request (dict): A dictionary containing 'object_type', 'identifier' as the venue_id.

    Returns:
        A tuple containing a boolean indicating success, and either the list of events or an error message.
    """
    # Extract venue_id from request
    venue_id = request["identifier"]

    try:
        # Call the RPC function without requested_attributes
        response = supabase.rpc(
            "get_events_for_venue", {"venue_user_id": venue_id}
        ).execute()

        if hasattr(response, "data"):
            # Check if 'data' is not empty
            if response.data:
                return True, {"message": "Events found", "data": response.data}
            else:
                return True, {"message": "No events found", "data": []}
        else:
            # Handle the case where 'data' attribute is missing or response is not as expected
            return False, {"message": "Unexpected response format", "data": []}
    except Exception as e:
        return False, {"message": f"An API error occurred: {str(e)}", "data": []}


def get_events_for_artist(request):
    """
    Queries all events for a given artist from the 'events' table in the Supabase database using a request JSON
        structure.

    Args:
        request (dict): A dictionary containing 'object_type' and 'identifier' as the artist_id.

    Returns:
        A tuple containing a boolean indicating success, and either the list of events or an error message.
    """
    artist_id = request["identifier"]

    try:
        # Assuming the supabase.rpc() correctly calls the RPC function and returns a response object
        response = supabase.rpc(
            "get_events_for_artist", {"artist_id": artist_id}
        ).execute()

        if hasattr(response, "data"):
            # Check if 'data' is not empty
            if response.data:
                return True, {"message": "Events found", "data": response.data}
            else:
                return True, {"message": "No events found", "data": []}
        else:
            # Handle the case where 'data' attribute is missing or response is not as expected
            return False, {"message": "Unexpected response format", "data": []}
    except Exception as e:
        return False, {"message": f"An API error occurred: {str(e)}", "data": []}


def get_events_for_attendee(request):
    """
    Queries all events for a given attendee from the 'events' table in the Supabase database using a request JSON
        structure.

    Args:
        request (dict): A dictionary containing 'object_type', 'identifier' as the attendee_id.

    Returns:
        A tuple containing a boolean indicating success, and either the list of events and tickets or an error message.
    """
    # Extract attendee_id from request
    attendee_id = request["identifier"]

    try:
        # Call the RPC function with attendee_id
        response = supabase.rpc(
            "get_events_for_attendee", {"_attendee_id": attendee_id}
        ).execute()

        # Access the 'data' attribute directly from the SingleAPIResponse object
        if hasattr(response, "data"):
            # Check if 'data' is not empty
            if response.data:
                return True, {"message": "Events found", "data": response.data}
            else:
                return True, {"message": "No events found", "data": []}
        else:
            # Handle the case where 'data' attribute is missing or response is not as expected
            return False, {"message": "Unexpected response format", "data": []}
    except Exception as e:
        return False, {"message": f"An API error occurred: {str(e)}", "data": []}


def get_events_in_city(request):
    """
    Queries all events in a specified city from the 'events' table in the Supabase database using
        a request JSON structure.

    Args:
        request (dict): A dictionary containing 'object_type' and 'identifier' as the city name.

    Returns:
        A tuple containing a boolean indicating success, and either the list of events or an error message.
    """
    # Extract city name from request
    try:
        city_name = request.get("identifier", None)
    except Exception as e:
        return {"message": f"Error getting identifier: {e}", "data": []}
    if not city_name:
        return False, {"message": "City name is required", "data": []}
    try:
        # Call the RPC function with city_name
        response = supabase.rpc(
            "get_events_in_city", {"city_name": city_name}
        ).execute()

        if hasattr(response, "data"):
            # Check if 'data' is not empty
            if response.data:
                return True, {"message": "Events found", "data": response.data}
            else:
                return True, {"message": "No events found", "data": []}
        else:
            # Handle the case where 'data' attribute is missing or response is not as expected
            return False, {"message": "Unexpected response format", "data": []}
    except Exception as e:
        return False, {"message": f"An API error occurred: {str(e)}", "data": []}


def get_cities_by_country(request):
    """
    Queries all cities from the 'cities' table in the Supabase database
    for a given country using a request JSON structure.

    Args:
        request (dict): A dictionary containing 'object_type', 'identifier', and 'country' as the country name.

    Returns:
        A tuple containing a boolean indicating success, and either the list of cities or an error message.
    """
    try:
        country_name = request["identifier"]
        if not country_name:
            return False, {"message": "Country name is required", "data": []}
        response = (
            supabase.from_("cities").select("*").eq("country", country_name).execute()
        )

        if hasattr(response, "data") and response.data:
            cities = [city["city"] for city in response.data]  # Extracting city names
            return True, {"message": "Cities found", "data": cities}
        else:
            # Handle empty or unexpected response
            return True, {
                "message": "No cities found or unexpected response format",
                "data": [],
            }
    except Exception as e:
        # Handle exceptions, such as connection errors or query failures
        return False, {"message": f"An API error occurred: {str(e)}", "data": []}


def apply_for_gig(event_id, user_id):
    """
    Adds artist's user_id to the array of pending applicants for an event.

    Args:
        request (dict): A dictionary containing 'event_id' and 'user_id'.

    Returns:
        A tuple containing a boolean indicating success, and either a success message or an error message.
    """
    try:
        response = supabase.rpc(
            "apply_for_gig", {"target_event_id": event_id, "applicant_user_id": user_id}
        ).execute()
        print(response)
        if response.data:
            return True, "Application submitted successfully."
        else:
            return False, "Failed to submit application."
    except Exception as e:
        return False, f"An exception occurred: {str(e)}"


@functions_framework.http
def api_create_event(request):
    request_data = request.json

    if "function" not in request_data or request_data["function"] != "create":
        return jsonify({"error": "API only handles create requests"}), 400

    event_id, message = create_event(request_data)
    if event_id:
        return jsonify({"message": message, "data": event_id}), 200
    else:
        return jsonify({"error": message}), 400


@functions_framework.http
def api_update_event(request):
    request_data = request.json

    if "function" not in request_data or request_data["function"] != "update":
        return jsonify({"error": "API only handles update requests"}), 400

    event_id = request_data.get("event_id")
    update_attributes = request_data.get("update_attributes")

    success, message = update_event(event_id, update_attributes)
    if success:
        return jsonify({"message": message}), 200
    else:
        return jsonify({"error": message}), 400


@functions_framework.http
def api_delete_event(request):
    request_data = request.json

    if "function" not in request_data or request_data["function"] != "delete":
        return jsonify({"error": "API only handles delete requests"}), 400

    success, message = delete_event(request_data)
    if success:
        return jsonify({"message": message}), 200
    else:
        return jsonify({"error": message}), 400


@functions_framework.http
def api_get_event_info(request):
    request_data = request.get_json()

    # Check a valid payload was received
    if not request_data:
        return jsonify({"error": "Invalid or missing JSON payload"}), 400

    if "function" not in request_data or request_data["function"] != "get":
        return jsonify({"error": "API only handles get requests"}), 400

    event_id = request_data.get("event_id")
    attributes = request_data.get("attributes")

    # Call function
    result = get_event_info(event_id, attributes)

    # Handle outcomes
    if "error" in result:
        return (
            jsonify(result),
            (
                404
                if result["error"] == "No account found for the provided email."
                else 500
            ),
        )

    return jsonify(result), 200


@functions_framework.http
def api_get_events_for_venue(request):
    request_data = request.json
    success, message = get_events_for_venue(request_data)
    if success:
        return jsonify({"message": message}), 200
    else:
        return jsonify({"error": message}), 400


@functions_framework.http
def api_get_events_in_city(request):
    request_data = request.get_json()
    success, message = get_events_in_city(request_data)
    if success:
        return jsonify({"message": message}), 200
    else:
        return jsonify({"error": message}), 400


@functions_framework.http
def api_get_events_for_artist(request):
    request_data = request.json
    success, message = get_events_for_artist(request_data)
    if success:
        return jsonify({"message": message}), 200
    else:
        return jsonify({"error": message}), 400


@functions_framework.http
def api_get_events_for_attendee(request):
    request_data = request.json
    success, message = get_events_for_attendee(request_data)
    if success:
        return jsonify({"message": message}), 200
    else:
        return jsonify({"error": message}), 400


@functions_framework.http
def api_get_cities_by_country(request):
    request_data = request.json

    success, message = get_cities_by_country(request_data)
    if success:
        return jsonify({"message": message}), 200
    else:
        return jsonify({"error": message}), 400


@functions_framework.http
def api_apply_for_gig(request):
    request_data = request.json

    if not request_data["identifier"]:
        return jsonify({"message": "Missing event_id."}), 400
    if not request_data["artist_id"]:
        return jsonify({"message": "Missing artist_id."}), 400

    success, message = apply_for_gig(request_data["identifier"])
    if success:
        return jsonify({"message": message}), 200
    else:
        return jsonify({"error": message}), 400


# if __name__ == "__main__":
# req = {"function": "get", "object_type": "city", "identifier": "United States"}
# success, message = get_cities_by_country(req)
# print(success)
# print(message)
# app.run(debug=True)
#
# create_req = {
#     "function": "create",
#     "object_type": "event",
#     "identifier": "1234345256345635",
#     "attributes": {
#         "venue_id": "1234345256345635",
#         "event_name": "Yaml sesh",
#         "date_time": "24 March 2024",
#         "total_tickets": 1,
#         "sold_tickets": 0,
#         "artist_ids": ["105165436154430421986"],
#     },
# }
# id, message = create_event(create_req)
# print(id)
# print(message)
#
# get_artist_events_req = {
#     "function": "get",
#     "object_type": "event",
#     "identifier": "105165436154430421986",  # artist_id
# }
# success, message = get_events_for_artist(get_artist_events_req)
# print(success)
# print(message)
#
# get_venue_events_req = {
#     "function": "get",
#     "object_type": "event",
#     "identifier": "1234345256345635",  # venue_id
# }
# success, message = get_events_for_venue(get_venue_events_req)
# print(success)
# print(message)
#
# get_attendee_events_req = {
#     "function": "get",
#     "object_type": "event",
#     "identifier": "105165436154430421986",  # attendee_id
# }
# success, message = get_events_for_attendee(get_attendee_events_req)
# print(success)
# print(message)
#
# get_city_events_req = {
#     "function": "get",
#     "object_type": "event",
#     "identifier": "Juliopolis",  # city_name
# }
# success, message = get_events_in_city(get_city_events_req)
# print(success)
# print(message)
#
# get_req = {
#     "function": "get",
#     "object_type": "event",
#     "identifier": id,
#     "attributes": {
#         "venue_id": True,
#         "event_name": True,
#         "date_time": True,
#         "total_tickets": True,
#         "sold_tickets": True,
#         "artist_ids": True,
#     },
# }
# success, message = get_event_info(get_req)
# print(success)
# print(message)
#
# update_req = {
#     "function": "update",
#     "object_type": "event",
#     "identifier": id,
#     "attributes": {
#         "venue_id": "1234345256345635",
#         "event_name": "Yaml sesh 2.0",
#         "date_time": "2024-03-25T02:05:00+00:00",
#         "total_tickets": 1,
#         "sold_tickets": 0,
#         "artist_ids": ["105165436154430421986"],
#     },
# }
# id, message = update_event(update_req)
# print(id)
# print(message)
#
# delete_req = {
#     "function": "delete",
#     "object_type": "event",
#     "identifier": id,
#     "attributes": {},
# }
# id, message = delete_event(update_req)
# print(id)
# print(message)
