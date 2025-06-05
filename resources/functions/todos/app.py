import json
import os
import uuid

import boto3

TABLE_NAME = os.environ.get("TABLE_NAME")
BUCKET_NAME = os.environ.get("BUCKET_NAME")

dynamodb = boto3.resource("dynamodb")
todo_table = dynamodb.Table(TABLE_NAME)


def create_todo(event, context):
    try:
        body = json.loads(event.get("body", "{}"))

        title = body.get("title")
        if not title:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(
                    {"message": 'Validation Error: "title" is required.'}
                ),
            }

        completed = bool(body.get("completed", False))

        todo_id = str(uuid.uuid4())

        todo_table.put_item(
            Item={
                "todo_id": todo_id,
                "title": title,
                "completed": completed,
            }
        )

        return {
            "statusCode": 201,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(
                {
                    "todo_id": todo_id,
                    "title": title,
                    "completed": completed,
                }
            ),
        }

    except json.JSONDecodeError:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": "Invalid JSON in request body."}),
        }
    except Exception as e:
        print(f"Error creating todo: {e}")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": "Internal Server Error."}),
        }


def get_todos(event, context):
    try:
        response = todo_table.scan()
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(response["Items"]),
        }
    except Exception as e:
        print(f"Error getting todos: {e}")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": "Internal Server Error."}),
        }


def get_todo(event, context):
    try:
        todo_id = event.get("pathParameters", {}).get("todo_id")
        if not todo_id:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(
                    {"message": 'Validation Error: "todo_id" is required.'}
                ),
            }

        response = todo_table.get_item(Key={"todo_id": todo_id})
        if "Item" not in response:
            return {
                "statusCode": 404,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"message": "Todo not found."}),
            }
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(response["Item"]),
        }
    except Exception as e:
        print(f"Error getting todo: {e}")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": "Internal Server Error."}),
        }
