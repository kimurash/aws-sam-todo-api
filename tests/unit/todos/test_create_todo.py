import json
import os

import boto3
import pytest
from moto import mock_aws


@pytest.fixture(scope="module")
def aws_credentials():
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "ap-northeast-1"


@pytest.fixture(scope="function")
def setup_lambda_environment(aws_credentials):
    with mock_aws():
        table_name = "test-todo-table"
        bucket_name = "test-bucket"

        os.environ["TABLE_NAME"] = table_name
        os.environ["BUCKET_NAME"] = bucket_name

        dynamodb = boto3.resource("dynamodb", region_name="ap-northeast-1")
        dynamodb.create_table(
            TableName=table_name,
            KeySchema=[{"AttributeName": "todo_id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "todo_id", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )

        from resources.functions.todos import app as todo_app

        yield todo_app, dynamodb.Table(table_name)

        os.environ.pop("TABLE_NAME", None)
        os.environ.pop("BUCKET_NAME", None)


def test_create_todo_success(setup_lambda_environment):
    todo_app, todo_table = setup_lambda_environment

    request_body = {
        "title": "Test Todo Title",
        "completed": False,
    }

    event = {
        "body": json.dumps(request_body),
    }
    response = todo_app.create_todo(event, {})

    assert response["statusCode"] == 201
    assert response["headers"]["Content-Type"] == "application/json"

    body = json.loads(response["body"])
    assert body["title"] == request_body["title"]
    assert body["completed"] == request_body["completed"]

    item = todo_table.get_item(Key={"todo_id": body["todo_id"]}).get("Item")
    assert item is not None


def test_create_todo_missing_title(setup_lambda_environment):
    todo_app, _ = setup_lambda_environment
    event = {
        "body": json.dumps({"completed": True}),
    }

    response = todo_app.create_todo(event, {})

    assert response["statusCode"] == 400
    assert response["headers"]["Content-Type"] == "application/json"


def test_create_todo_empty_body(setup_lambda_environment):
    todo_app, _ = setup_lambda_environment
    event = {
        "body": json.dumps({}),
    }

    response = todo_app.create_todo(event, {})

    assert response["statusCode"] == 400
    assert response["headers"]["Content-Type"] == "application/json"


def test_create_todo_no_body(setup_lambda_environment):
    todo_app, _ = setup_lambda_environment

    response = todo_app.create_todo({}, {})

    assert response["statusCode"] == 400
    assert response["headers"]["Content-Type"] == "application/json"


def test_create_todo_invalid_json(setup_lambda_environment):
    todo_app, _ = setup_lambda_environment
    event = {
        "body": "{invalid json",
    }

    response = todo_app.create_todo(event, {})

    assert response["statusCode"] == 400
    assert response["headers"]["Content-Type"] == "application/json"


def test_create_todo_dynamodb_error(setup_lambda_environment, monkeypatch):
    todo_app, todo_table = setup_lambda_environment

    def mock_put_item(*args, **kwargs):
        raise Exception()

    monkeypatch.setattr(todo_app.todo_table, "put_item", mock_put_item)

    event = {
        "body": json.dumps({"title": "Test Todo Title"}),
    }

    response = todo_app.create_todo(event, {})

    assert response["statusCode"] == 500
    assert response["headers"]["Content-Type"] == "application/json"
