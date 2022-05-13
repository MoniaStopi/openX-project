import requests
import json
from cerberus import Validator
import re

url = "https://restful-booker.herokuapp.com"
headers = {"Content-Type": "application/json", "Accept": "application/json"}

input_type_schema = {
    "firstname": {"type": "string"},
    "lastname": {"type": "string"},
    "totalprice": {"type": "number"},
    "depositpaid": {"type": "boolean"},
    "bookingdates": {
        "type": "dict",
        "schema": {"checkin": {"type": "string"}, "checkout": {"type": "string"}},
    },
    "additionalneeds": {"type": "string"},
}

update_data = {
    "firstname": "James",
    "lastname": "Brown",
    "totalprice": 111,
    "depositpaid": True,
    "bookingdates": {"checkin": "2018-01-01", "checkout": "2019-01-01"},
    "additionalneeds": "Breakfast",
}
partial_update_data = {
    "firstname": "Alicja",
    "lastname": "Brown",
    "bookingdates": {"checkin": "2018-12-01", "checkout": "2019-01-01"},
}


def get_token(url: str) -> dict:
    url = f"{url}/auth"
    post_data = {"username": "admin", "password": "password123"}
    response = requests.post(url, data=json.dumps(post_data), headers=headers)
    return response.json()


token = get_token(url)


def check_format_date(date_data):
    return bool(re.match("20[0-9][0-9]-[0-1][0-9]-[0-3][0-9]", date_data))


def test_auth_create_token(url: str):
    url = f"{url}/auth"
    post_data = {"username": "admin", "password": "password123"}
    response = requests.post(url, data=json.dumps(post_data), headers=headers)

    assert response.status_code == 200
    assert "token" in response.json()


def test_get_all_booking_ids(url: str):
    response = requests.get(f"{url}/booking", headers=headers)
    assert response.status_code == 200
    assert response.json()


def test_get_user_booking_id(url: str, first_name: str, last_name: str):
    response = requests.get(
        f"{url}/booking?firstname={first_name}&lastname={last_name}", headers=headers
    )

    assert response.status_code == 200


def test_get_booking_by_id(url: str, id: int):
    response = requests.get(f"{url}/booking/{id}", headers=headers)
    checkin = response.json()["bookingdates"]["checkin"]
    checkout = response.json()["bookingdates"]["checkout"]
    booking_data = json.loads(response.text)
    validator = Validator(input_type_schema, require_all=True)
    is_valid = validator.validate(booking_data)


    assert is_valid
    assert response.status_code == 200
    assert check_format_date(checkin) & check_format_date(checkout)


def test_update_booking(url: str, id: int, update_data: dict):
    response = requests.put(
        f"{url}/booking/{id}",
        data=json.dumps(update_data),
        cookies=token,
        headers=headers,
    )
    checkin = response.json()["bookingdates"]["checkin"]
    checkout = response.json()["bookingdates"]["checkout"]
    booking_data = json.loads(response.text)

    validator = Validator(input_type_schema, require_all=True)
    is_valid = validator.validate(booking_data)

    assert is_valid
    assert response.status_code == 200
    assert check_format_date(checkin) & check_format_date(checkout)
    assert response.json()["lastname"] == update_data["lastname"]
    assert response.json()["totalprice"] == update_data["totalprice"]


def test_partial_update_booking(url: str, id: int, partial_update_data: dict):
    response = requests.patch(
        f"{url}/booking/{id}",
        data=json.dumps(partial_update_data),
        cookies=token,
        headers=headers,
    )
    checkin = response.json()["bookingdates"]["checkin"]
    checkout = response.json()["bookingdates"]["checkout"]

    assert response.status_code == 200
    assert check_format_date(checkin) & check_format_date(checkout)
    assert response.json()["firstname"] == partial_update_data["firstname"]
    assert response.json()["lastname"] == partial_update_data["lastname"]


def test_delete_data_by_id(url: str, id: int):
    response = requests.delete(f"{url}/booking/{id}", cookies=token, headers=headers)

    assert response.status_code == 201


def test_ping_health(url: str):
    response = requests.get(f"{url}/ping", headers=headers)

    assert response.status_code == 201


if __name__ == "__main__":
    test_get_all_booking_ids(url)
    test_get_booking_by_id(url,80)
    test_get_user_booking_id(url, 'Sally', 'Brown')
    test_auth_create_token(url)
    test_update_booking(url,224, update_data)
    test_partial_update_booking(url,224,partial_update_data)
    #test_delete_data_by_id(url, 1552)
    test_ping_health(url)
