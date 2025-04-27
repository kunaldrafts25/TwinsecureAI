import requests
from typing import Optional # Import Optional for type hinting

# Import settings if the webhook URL comes from config
# from app.core.config import settings

def send_slack_message(message: str, webhook_url: str) -> Optional[requests.Response]:
    """
    Sends a message to a Slack channel using an incoming webhook.

    Args:
        message: The text content of the message to send.
        webhook_url: The Slack incoming webhook URL.

    Returns:
        The requests.Response object if the request was successful,
        None otherwise.
    """
    # Prepare the payload for the Slack message
    payload = {
        "text": message
    }

    try:
        # Send the HTTP POST request to the Slack webhook URL
        response = requests.post(webhook_url, json=payload)

        # Raise an exception for bad status codes (4xx or 5xx)
        response.raise_for_status()

        print(f"Slack message sent successfully. Status code: {response.status_code}")
        return response

    except requests.exceptions.RequestException as e:
        # Handle any errors that occur during the request
        print(f"Failed to send Slack message: {e}")
        return None
    except Exception as e:
        # Catch any other unexpected errors
        print(f"An unexpected error occurred while sending Slack message: {e}")
        return None

# You might have other functions related to Slack integration here,
# for example, formatting messages, handling different message types, etc.

# Example usage (for testing purposes, not typically run directly)
# if __name__ == "__main__":
#     # Replace with a real webhook URL for testing
#     test_webhook_url = "YOUR_SLACK_WEBHOOK_URL_HERE"
#     test_message = "Hello from the backend application!"
#
#     if "YOUR_SLACK_WEBHOOK_URL_HERE" in test_webhook_url:
#          print("Please replace 'YOUR_SLACK_WEBHOOK_URL_HERE' with your actual Slack webhook URL to test.")
#     else:
#         print(f"Attempting to send test message: '{test_message}'")
#         send_slack_message(test_message, test_webhook_url)
