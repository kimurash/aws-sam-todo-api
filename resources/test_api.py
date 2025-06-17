import json
import traceback

import inquirer
import requests
from faker import Faker

fake = Faker("ja_JP")


class APITester:

    def __init__(self, base_url: str):
        self.base_url = base_url

    def _report_result(self, response: requests.Response, expected_status: int) -> None:
        if response.status_code == expected_status:
            print("✅ Passed")
        else:
            print("❌ Failed")

        print(f"Status Code: {response.status_code}")
        print("Response Body:")
        try:
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        except json.JSONDecodeError:
            print(response.text)

    def create_todo(self):
        print("Testing POST /todos")

        url = f"{self.base_url}/todos"
        payload = {"title": fake.word(), "completed": False}

        response = requests.post(url, json=payload)
        self._report_result(response, 201)

        if response.status_code == 201:
            data = response.json()
            self.todo_id = data.get("todo_id")

    def get_all_todos(self):
        print("Testing GET /todos")

        url = f"{self.base_url}/todos"
        response = requests.get(url)
        self._report_result(response, 200)

    def get_todo(self):
        if not self.todo_id:
            print("Create Todo first.")
            return

        print("Testing GET /todos/{todo_id}")

        url = f"{self.base_url}/todos/{self.todo_id}"
        response = requests.get(url)

        self._report_result(response, 200)

    def update_todo(self):
        if not self.todo_id:
            print("Create Todo first.")
            return

        print("Testing PUT /todos/{todo_id}")

        url = f"{self.base_url}/todos/{self.todo_id}"
        payload = {"title": fake.word(), "completed": False}

        response = requests.put(url, json=payload)
        self._report_result(response, 200)

    def delete_todo(self):
        if not self.todo_id:
            print("Create Todo first.")
            return

        print("Testing DELETE /todos/{todo_id}")

        url = f"{self.base_url}/todos/{self.todo_id}"

        response = requests.delete(url)
        self._report_result(response, 204)

        if response.status_code == 204:
            self.todo_id = None

    def generate_upload_url(self):
        print("Testing GET /images/presigned-url")

        url = f"{self.base_url}/images/presigned-url"

        response = requests.get(url, params={"format": "jpg"})
        self._report_result(response, 200)

    def run(self):
        testcase = {
            "1. Test POST /todos": self.create_todo,
            "2. Test GET /todos": self.get_all_todos,
            "3. Test GET /todos/{todo_id}": self.get_todo,
            "5. Test PUT /todos/{todo_id}": self.update_todo,
            "6. Test DELETE /todos/{todo_id}": self.delete_todo,
            "7. Test GET /images/presigned-url": self.generate_upload_url,
            "Exit": None,
        }

        while True:
            questions = [
                inquirer.List(
                    "test",
                    message="Select a test case to run:",
                    choices=list(testcase.keys()),
                    carousel=True,
                )
            ]

            try:
                answer = inquirer.prompt(questions)
                if answer["test"] == "Exit":
                    break

                test_function = testcase[answer["test"]]
                test_function()

            except requests.exceptions.ConnectionError:
                print(requests.exceptions.ConnectionError)
                break
            except KeyboardInterrupt:
                break
            except Exception:
                print(traceback.format_exc())


if __name__ == "__main__":
    BASE_URL = "http://127.0.0.1:3000"
    tester = APITester(base_url=BASE_URL)
    tester.run()
