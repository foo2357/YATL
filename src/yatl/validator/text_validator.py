from requests import Response


def validate_text_body(response: Response, expected_text: str) -> None:
    """Validates that the plain-text response contains a given substring.

    Args:
        response: The HTTP response with text content.
        expected_text: The substring that must appear in the response body.

    Raises:
        AssertionError: If the substring is not found.
    """
    actual_text = response.text
    if expected_text not in actual_text:
        raise AssertionError(f"Expected text '{expected_text}' not found in response")
