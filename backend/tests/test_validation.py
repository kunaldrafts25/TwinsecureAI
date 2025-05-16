"""
Test script to check if validation functions work.
"""

from app.services.validation import validate_email, validate_hostname, validate_ip


def test_validate_ip():
    """Test IP validation."""
    # Valid IPs
    assert validate_ip("192.168.1.1") == True
    assert validate_ip("10.0.0.1") == True
    assert validate_ip("2001:0db8:85a3:0000:0000:8a2e:0370:7334") == True

    # Invalid IPs
    assert validate_ip("256.256.256.256") == False
    assert validate_ip("not_an_ip") == False
    assert validate_ip("") == False

    print("All IP validation tests passed!")


def test_validate_email():
    """Test email validation."""
    # Valid emails
    assert validate_email("user@example.com") == True
    assert validate_email("user.name+tag@example.co.uk") == True

    # Invalid emails
    assert validate_email("not_an_email") == False
    assert validate_email("@example.com") == False
    assert validate_email("user@") == False
    assert validate_email("") == False

    print("All email validation tests passed!")


def test_validate_hostname():
    """Test hostname validation."""
    # Valid hostnames
    assert validate_hostname("example.com") == True
    assert validate_hostname("sub.example.com") == True
    assert validate_hostname("example") == True

    # Invalid hostnames
    assert validate_hostname("example..com") == False
    assert validate_hostname("-example.com") == False
    assert validate_hostname("") == False

    print("All hostname validation tests passed!")


if __name__ == "__main__":
    test_validate_ip()
    test_validate_email()
    test_validate_hostname()
    print("All validation tests passed!")
