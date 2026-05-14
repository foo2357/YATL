from typing import Any

from lxml import etree
from requests import Response


def validate_xml_body(response: Response, expected_xml: dict[str, Any]) -> None:
    """Validates that the XML response contains elements with expected text.

    Args:
        response: The HTTP response containing XML data.
        expected_xml: A dictionary mapping XPath expressions to expected
            text values.

    Raises:
        AssertionError: If the response is not valid XML, an XPath matches
            no elements, or the text of the first matching element differs.
    """
    try:
        root = etree.fromstring(response.content)
    except etree.XMLSyntaxError:
        raise AssertionError("Response is not valid XML")
    for xpath, expected_value in expected_xml.items():
        elements = root.xpath(xpath)
        if not elements:
            raise AssertionError(f"XML element with xpath '{xpath}' not found")
        actual = elements[0].text
        if actual != expected_value:
            raise AssertionError(
                f"XML element '{xpath}' expected '{expected_value}', got '{actual}'"
            )
