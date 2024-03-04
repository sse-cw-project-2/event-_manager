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
    "ticket": ["ticket_id", "event_id", "attendee_id", "price", "redeemed", "status"],
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
    attributes_to_check = request["attributes"]

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
        result = supabase.rpc("get_events_for_venue", {"venue_user_id": venue_id})

        if hasattr(result, "error") and result.error:
            return False, f"An error occurred while fetching events: {result.error}"
        elif not result.data:
            return False, "No events found for the provided venue ID."
        else:
            return True, result.data
    except Exception as e:
        return False, f"An exception occurred: {str(e)}"


def get_events_for_artist(request):
    """
    Queries all events for a given artist from the 'events' table in the Supabase database using a request JSON
        structure.

    Args:
        request (dict): A dictionary containing 'object_type' and 'identifier' as the artist_id.

    Returns:
        A tuple containing a boolean indicating success, and either the list of events or an error message.
    """
    # Extract artist_id from request
    artist_id = request["identifier"]

    try:
        # Call the RPC function with artist_id
        result = supabase.rpc("get_events_for_artist", {"artist_id": artist_id})

        print(result)

        if result.data:
            return True, {
                "message": "Events found",
                "data": result.data[0],
            }
        else:
            return False, {"message": "No events found", "data": []}
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
        result = supabase.rpc("get_events_for_attendee", {"attendee_id": attendee_id})

        if hasattr(result, "error") and result.error:
            return False, f"An error occurred while fetching events: {result.error}"
        elif not result.data:
            return False, "No events found for the provided attendee ID."
        else:
            return True, result.data
    except Exception as e:
        return False, f"An exception occurred: {str(e)}"


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
    city_name = request["identifier"]

    try:
        # Call the RPC function with city_name
        result = supabase.rpc("get_events_in_city", {"city_name": city_name})

        if hasattr(result, "error") and result.error:
            return False, f"An error occurred while fetching events: {result.error}"
        elif not result.data:
            return False, "No events found in the specified city."
        else:
            return True, result.data
    except Exception as e:
        return False, f"An exception occurred: {str(e)}"


@functions_framework.http
def api_create_event(request):
    request_data = request.json
    success, message = create_event(request_data)
    if success:
        return jsonify({"message": message}), 200
    else:
        return jsonify({"error": message}), 400


@functions_framework.http
def api_update_event(request):
    request_data = request.json

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

    event_id = request_data.get("event_id")
    attributes = request_data.get("attributes")

    # Call function
    result = get_event_info(event_id, attributes)

    # Handle outcomes
    if "error" in result:
        # Return 404 if account not found, or 500 for all other errors in reaching the database
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
    request_data = request.json
    success, message = get_events_in_city(request_data)
    if success:
        return jsonify({"message": message}), 200
    else:
        return jsonify({"error": message}), 400


@functions_framework.http
def api_get_events_for_artist(request):
    identifier = request.args.get('identifier')
    object_type = request.args.get('object_type')
    request_data = {
        "identifier": identifier,
        "object_type": object_type
    }
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


if __name__ == "__main__":
    app.run(debug=True)
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
    #
    # get_artist_events_req = {
    #     "function": "get",
    #     "object_type": "event",
    #     "identifier": "105165436154430421986",
    # }
    # success, message = get_events_for_artist(get_artist_events_req)
    # print(id)
    # print(message)


