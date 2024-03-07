####################################################################################################
# Project Name: Motive Event Management System
# Course: COMP70025 - Software Systems Engineering
# File: testEventManager.py
# Description: This file contains unit tests for each function in the eventManager.py file.
#
# Authors: James Hartley, Ankur Desai, Patrick Borman, Julius Gasson, and Vadim Dunaevskiy
# Date: 2024-03-04
# Version: 1.2
#
# Changes: Added unit tests for RPCs.
#
# Notes:
####################################################################################################


import unittest
from unittest.mock import patch, Mock, MagicMock

from main import (
    get_events_for_venue,
    get_events_for_artist,
    get_events_for_attendee,
    get_events_in_city,
    get_event_info,
    delete_event,
    create_event,
    apply_for_gig,
    handle_gig_application,
)


class TestGetEventsForVenue(unittest.TestCase):
    @patch("main.supabase")
    def test_events_found(self, mock_supabase):
        # Mocking the response object with data attribute
        mock_response = Mock()
        mock_response.data = [{"event_id": "123", "event_name": "Test Event"}]
        mock_supabase.rpc().execute.return_value = mock_response

        request = {"identifier": "venue123"}
        success, response = get_events_for_venue(request)

        self.assertTrue(success)
        self.assertIn("Events found", response["message"])
        self.assertEqual(len(response["data"]), 1)
        self.assertEqual(response["data"][0]["event_id"], "123")

    @patch("main.supabase")
    def test_no_events_found(self, mock_supabase):
        # Mocking the response object with empty data
        mock_response = Mock()
        mock_response.data = []
        mock_supabase.rpc().execute.return_value = mock_response

        request = {"identifier": "venue123"}
        success, response = get_events_for_venue(request)

        self.assertTrue(success)
        self.assertIn("No events found", response["message"])

    @patch("main.supabase")
    def test_unexpected_response_format(self, mock_supabase):
        # Mocking the response object without data attribute
        mock_response = Mock()
        del mock_response.data  # Simulate missing 'data' attribute
        mock_supabase.rpc().execute.return_value = mock_response

        request = {"identifier": "venue123"}
        success, response = get_events_for_venue(request)

        self.assertFalse(success)
        self.assertIn("Unexpected response format", response["message"])

    @patch("main.supabase")
    def test_exception_during_rpc_call(self, mock_supabase):
        # Simulating an exception during RPC call
        mock_supabase.rpc().execute.side_effect = Exception("RPC call failed")

        request = {"identifier": "venue123"}
        success, response = get_events_for_venue(request)

        self.assertFalse(success)
        self.assertIn("An API error occurred", response["message"])


class TestGetEventsForArtist(unittest.TestCase):
    @patch("main.supabase")
    def test_events_found(self, mock_supabase):
        # Mock the response object for a successful data retrieval
        mock_response = Mock()
        mock_response.data = [{"event_id": "abc123", "event_name": "Art Show"}]
        mock_supabase.rpc().execute.return_value = mock_response

        request = {"identifier": "artist123"}
        success, response = get_events_for_artist(request)

        self.assertTrue(success)
        self.assertIn("Events found", response["message"])
        self.assertEqual(len(response["data"]), 1)
        self.assertEqual(response["data"][0]["event_id"], "abc123")

    @patch("main.supabase")
    def test_no_events_found(self, mock_supabase):
        # Mock the response object for no data
        mock_response = Mock()
        mock_response.data = []
        mock_supabase.rpc().execute.return_value = mock_response

        request = {"identifier": "artist123"}
        success, response = get_events_for_artist(request)

        self.assertTrue(success)
        self.assertIn("No events found", response["message"])

    @patch("main.supabase")
    def test_unexpected_response_format(self, mock_supabase):
        # Mock an unexpected response format
        mock_response = Mock()
        del mock_response.data  # Simulate missing 'data' attribute
        mock_supabase.rpc().execute.return_value = mock_response

        request = {"identifier": "artist123"}
        success, response = get_events_for_artist(request)

        self.assertFalse(success)
        self.assertIn("Unexpected response format", response["message"])

    @patch("main.supabase")
    def test_exception_during_rpc_call(self, mock_supabase):
        # Simulate an exception during the RPC call
        mock_supabase.rpc().execute.side_effect = Exception("RPC call failed")

        request = {"identifier": "artist123"}
        success, response = get_events_for_artist(request)

        self.assertFalse(success)
        self.assertIn("An API error occurred", response["message"])


class TestGetEventsForAttendee(unittest.TestCase):
    @patch("main.supabase")  # Adjust to match where you import supabase
    def test_events_found(self, mock_supabase):
        # Mock the response object for a successful data retrieval
        mock_response = Mock()
        mock_response.data = [{"event_id": "abc123", "event_name": "Concert"}]
        mock_supabase.rpc().execute.return_value = mock_response

        request = {"identifier": "attendee123"}
        success, response = get_events_for_attendee(request)

        self.assertTrue(success)
        self.assertIn("Events found", response["message"])
        self.assertEqual(len(response["data"]), 1)

    @patch("main.supabase")
    def test_no_events_found(self, mock_supabase):
        # Mock the response object for no data
        mock_response = Mock()
        mock_response.data = []
        mock_supabase.rpc().execute.return_value = mock_response

        request = {"identifier": "attendee123"}
        success, response = get_events_for_attendee(request)

        self.assertTrue(success)
        self.assertIn("No events found", response["message"])

    @patch("main.supabase")
    def test_unexpected_response_format(self, mock_supabase):
        # Mock a response object without 'data' attribute to simulate an unexpected format
        mock_response = Mock()
        delattr(mock_response, "data")
        mock_supabase.rpc().execute.return_value = mock_response

        request = {"identifier": "attendee123"}
        success, response = get_events_for_attendee(request)

        self.assertFalse(success)
        self.assertIn("Unexpected response format", response["message"])

    @patch("main.supabase")
    def test_exception_during_rpc_call(self, mock_supabase):
        # Simulate an exception during the RPC call
        mock_supabase.rpc().execute.side_effect = Exception("RPC call failed")

        request = {"identifier": "attendee123"}
        success, response = get_events_for_attendee(request)

        self.assertFalse(success)
        self.assertIn("An API error occurred", response["message"])


class TestGetEventsInCity(unittest.TestCase):
    @patch("main.supabase")
    def test_events_found(self, mock_supabase):
        # Mock the response object for a successful data retrieval
        mock_response = Mock()
        mock_response.data = [
            {
                "event_id": "def456",
                "event_name": "City Festival",
                "city_name": "Test City",
            }
        ]
        mock_supabase.rpc().execute.return_value = mock_response

        request = {"identifier": "Test City"}
        success, response = get_events_in_city(request)

        self.assertTrue(success)
        self.assertIn("Events found", response["message"])
        self.assertEqual(len(response["data"]), 1)

    @patch("main.supabase")
    def test_no_events_found(self, mock_supabase):
        # Mock the response object for no data
        mock_response = Mock()
        mock_response.data = []
        mock_supabase.rpc().execute.return_value = mock_response

        request = {"identifier": "Test City"}
        success, response = get_events_in_city(request)

        self.assertTrue(success)
        self.assertIn("No events found", response["message"])

    @patch("main.supabase")
    def test_unexpected_response_format(self, mock_supabase):
        # Mock a response object without 'data' attribute to simulate an unexpected format
        mock_response = Mock()
        delattr(mock_response, "data")
        mock_supabase.rpc().execute.return_value = mock_response

        request = {"identifier": "Test City"}
        success, response = get_events_in_city(request)

        self.assertFalse(success)
        self.assertIn("Unexpected response format", response["message"])

    @patch("main.supabase")
    def test_exception_during_rpc_call(self, mock_supabase):
        # Simulate an exception during the RPC call
        mock_supabase.rpc().execute.side_effect = Exception("RPC call failed")

        request = {"identifier": "Test City"}
        success, response = get_events_in_city(request)

        self.assertFalse(success)
        self.assertIn("An API error occurred", response["message"])


class TestGetEventInfo(unittest.TestCase):
    @patch("main.supabase")
    def test_event_found_with_attributes(self, mock_supabase):
        # Mock the response object for a successful data retrieval
        mock_response = Mock()
        mock_response.data = [{"event_id": "123", "event_name": "Concert"}]
        mock_supabase.table().select().eq().execute.return_value = mock_response

        request = {
            "object_type": "event",
            "identifier": "123",
            "attributes": {"event_name": True},
        }
        success, response = get_event_info(request)

        self.assertTrue(success)
        self.assertIn("Event found", response["message"])
        self.assertIn("event_name", response["data"])

    @patch("main.supabase")
    def test_no_event_found(self, mock_supabase):
        # Mock the response object for no data
        mock_response = Mock()
        mock_response.data = []
        mock_supabase.table().select().eq().execute.return_value = mock_response

        request = {
            "object_type": "event",
            "identifier": "nonexistent",
            "attributes": {"event_name": True},
        }
        success, response = get_event_info(request)

        self.assertFalse(success)
        self.assertIn("Event not found", response["message"])

    @patch("main.supabase")
    def test_exception_during_data_retrieval(self, mock_supabase):
        # Simulate an exception during data retrieval
        mock_supabase.table().select().eq().execute.side_effect = Exception(
            "Database error"
        )

        request = {
            "object_type": "event",
            "identifier": "123",
            "attributes": {"event_name": True},
        }
        success, response = get_event_info(request)

        self.assertFalse(success)
        self.assertIn("An API error occurred", response["message"])


class TestDeleteEvent(unittest.TestCase):
    @patch("main.supabase")
    def test_event_deletion_successful(self, mock_supabase):
        # Mock the response object to simulate successful deletion
        mock_response = Mock()
        mock_response.data = [1]  # Simulate 1 row affected/deleted
        mock_supabase.table().delete().eq().execute.return_value = mock_response

        request = {"object_type": "event", "identifier": "123"}
        success, message = delete_event(request)

        self.assertTrue(success)
        self.assertEqual(message, "Event deletion was successful.")

    @patch("main.supabase")
    def test_event_not_found(self, mock_supabase):
        # Mock the response object for no data (event not found or already deleted)
        mock_response = Mock()
        mock_response.data = []  # Simulate no rows affected/deleted
        mock_supabase.table().delete().eq().execute.return_value = mock_response

        request = {"object_type": "event", "identifier": "nonexistent"}
        success, message = delete_event(request)

        self.assertFalse(success)
        self.assertEqual(message, "Event not found or already deleted.")

    @patch("main.supabase")
    def test_exception_during_deletion(self, mock_supabase):
        # Simulate an exception during the deletion process
        mock_supabase.table().delete().eq().execute.side_effect = Exception(
            "Database error"
        )

        request = {"object_type": "event", "identifier": "123"}
        success, message = delete_event(request)

        self.assertFalse(success)
        self.assertIn("An exception occurred", message)


class TestCreateEvent(unittest.TestCase):
    @patch("main.supabase")
    def test_exception_during_creation(self, mock_supabase):
        # Simulate an exception during the event creation process
        mock_supabase.table().insert().execute.side_effect = Exception("Database error")

        request = {
            "object_type": "event",
            "attributes": {"event_name": "Exception Event", "date": "2023-01-01"},
        }
        event_id, message = create_event(request)

        self.assertIsNone(event_id)
        self.assertIn("An exception occurred", message)


class TestApplyForGig(unittest.TestCase):

    @patch("main.supabase")
    def test_apply_for_gig_success(self, mock_supabase):
        # Mock the response for a successful application
        mock_response = mock_supabase.rpc.return_value.execute.return_value
        mock_response.data = True  # Simulate successful data response

        success, message = apply_for_gig("event_id_example", "user_id_example")

        self.assertTrue(success)
        self.assertEqual(message, "Application submitted successfully.")

    @patch("main.supabase")
    def test_apply_for_gig_failure(self, mock_supabase):
        # Mock the response for a failed application
        mock_response = mock_supabase.rpc.return_value.execute.return_value
        mock_response.data = None  # Simulate failure or no data response

        success, message = apply_for_gig("event_id_example", "user_id_example")

        self.assertFalse(success)
        self.assertEqual(message, "Failed to submit application.")

    @patch("main.supabase")
    def test_apply_for_gig_exception(self, mock_supabase):
        # Mock an exception being raised during the application
        mock_supabase.rpc.return_value.execute.side_effect = Exception("Test exception")

        success, message = apply_for_gig("event_id_example", "user_id_example")

        self.assertFalse(success)
        self.assertTrue("An exception occurred: Test exception" in message)


class TestHandleGigApplication(unittest.TestCase):

    @patch("main.supabase")
    def test_handle_gig_application_accept_success(self, mock_supabase):
        # Mock the response for a successful acceptance
        mock_response = mock_supabase.rpc.return_value.execute.return_value
        mock_response.data = True  # Simulate successful data response for acceptance

        success, message = handle_gig_application(
            "event_id_example", "user_id_example", accept=True
        )

        self.assertTrue(success)
        self.assertEqual(message, "Application accepted successfully.")

    @patch("main.supabase")
    def test_handle_gig_application_reject_success(self, mock_supabase):
        # Mock the response for a successful rejection
        mock_response = mock_supabase.rpc.return_value.execute.return_value
        mock_response.data = True  # Simulate successful data response for rejection

        success, message = handle_gig_application(
            "event_id_example", "user_id_example", accept=False
        )

        self.assertTrue(success)
        self.assertEqual(message, "Application rejected successfully.")

    @patch("main.supabase")
    def test_handle_gig_application_failure(self, mock_supabase):
        # Mock the response for a failed operation
        mock_response = mock_supabase.rpc.return_value.execute.return_value
        mock_response.data = None  # Simulate failure or no data response

        success, message = handle_gig_application(
            "event_id_example", "user_id_example", accept=True
        )

        self.assertFalse(success)
        self.assertEqual(message, "Failed to handle application.")

    @patch("main.supabase")
    def test_handle_gig_application_exception(self, mock_supabase):
        # Mock an exception being raised during the operation
        mock_supabase.rpc.return_value.execute.side_effect = Exception("Test exception")

        success, message = handle_gig_application(
            "event_id_example", "user_id_example", accept=True
        )

        self.assertFalse(success)
        self.assertTrue("An exception occurred: Test exception" in message)


if __name__ == "__main__":
    unittest.main()
