import unittest
from run import app


# Basic Unit Testing

class FlaskTest(unittest.TestCase):
    # Checking if Response is 200
    def test_response(self):
        test = app.test_client(self)
        response = test.get("/course/200")
        status = response.status_code
        self.assertEqual(status, 200)

    # Checking api returning Json Object
    def test_filter_page(self):
        test = app.test_client(self)
        response = test.get("course?page-number=20&page-size=10")
        self.assertEqual(response.content_type, 'application/json')

    # Checking api returning Json Object
    def test_filter_title(self):
        test = app.test_client(self)
        response = test.get("course?title-words=An")
        self.assertEqual(response.content_type, 'application/json')

    # Checking api returning Json Object
    def test_content_type(self):
        test = app.test_client(self)
        response = test.get("/course/200")
        self.assertEqual(response.content_type, 'application/json')

    # Sending incomplete required fields on create course route so it should return error
    def test_create_course_error(self):
        test = app.test_client()
        sent = {"description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor "
                               "incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud "
                               "exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure "
                               "dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla "
                               "pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia "
                               "deserunt mollit anim id est laborum.",
                "discount_price": 5,
                "price": 12,
                "image_path": "images/some/path/foo.jpg",
                "on_discount": False}
        response = test.post("course", json=sent)
        # Checking is it returning error
        self.assertTrue(b'error' in response.data)

    # Sending complete required fields on create course route so it should return json object
    def test_create_course(self):
        test = app.test_client()
        sent = {"description": "This is a brand new course",
                "discount_price": 5,
                "title": "Brand new course",
                "price": 25,
                "image_path": "images/some/path/foo.jpg",
                "on_discount": False}
        response = test.post("course", json=sent)
        self.assertTrue(b'id' in response.data)

    # Updating Course with invalid ID
    def test_update_course_error(self):
        test = app.test_client()
        sent = {"image_path": "images/some/path/foo.jpg",
                "discount_price": 5,
                "id": 0,
                "price": 25,
                "title": "Blah blah blah",
                "on_discount": False,
                "description": "New description"}
        response = test.put("/course/0", json=sent)
        self.assertTrue(b'error' in response.data)

    # Updating Course
    def test_update_course(self):
        test = app.test_client()
        sent = {"image_path": "images/some/path/foo.jpg",
                "discount_price": 5,
                "id": 10,
                "price": 25,
                "title": "Blah blah blah",
                "on_discount": False,
                "description": "New description"}
        response = test.put("/course/10", json=sent)
        self.assertTrue(b'id' in response.data)


if __name__ == '__main__':
    unittest.main()
