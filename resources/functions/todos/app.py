import json
import os
from typing import Any
import uuid

import boto3

TABLE_NAME = os.environ.get("TABLE_NAME")

dynamodb = boto3.resource("dynamodb", region_name="ap-northeast-1")
todo_table = dynamodb.Table(TABLE_NAME)


def create_todo(event: dict, context: Any):
    try:
        body = json.loads(event.get("body", "{}"))

        title = body.get("title")
        if not title:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"message": '"title" は必須項目です'}),
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
            "body": json.dumps({"message": "リクエストボディのデコードに失敗しました"}),
        }
    except Exception as e:
        print(f"Error creating todo: {e}")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": "サーバーの内部でエラーが発生しました"}),
        }


def get_todos(event: dict, context: Any) -> dict:
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
            "body": json.dumps({"message": "サーバーの内部でエラーが発生しました"}),
        }


def get_todo(event: dict, context: Any) -> dict:
    try:
        todo_id = event.get("pathParameters", {}).get("todo_id")
        if not todo_id:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"message": '"todo_id" は必須項目です'}),
            }

        response = todo_table.get_item(Key={"todo_id": todo_id})
        if "Item" not in response:
            return {
                "statusCode": 404,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"message": "Todoが見つかりませんでした"}),
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
            "body": json.dumps({"message": "サーバーの内部でエラーが発生しました"}),
        }


def update_todo(event: dict, context: Any) -> dict:
    try:
        todo_id = event.get("pathParameters", {}).get("todo_id")
        if not todo_id:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"message": '"todo_id" は必須項目です'}),
            }

        body = json.loads(event.get("body", "{}"))
        if not body:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"message": "更新する属性が指定されていません"}),
            }

        old_todo = todo_table.get_item(Key={"todo_id": todo_id})
        if "Item" not in old_todo:
            return {
                "statusCode": 404,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"message": "Todoが見つかりませんでした"}),
            }

        new_todo = old_todo["Item"].copy()
        new_todo.update(body)

        todo_table.put_item(Item=new_todo)

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(new_todo),
        }
    except json.JSONDecodeError:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": "リクエストボディのデコードに失敗しました"}),
        }
    except Exception as e:
        print(f"Error updating todo: {e}")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": "サーバーの内部でエラーが発生しました"}),
        }


def delete_todo(event: dict, context: Any) -> dict:
    try:
        todo_id = event.get("pathParameters", {}).get("todo_id")
        if not todo_id:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"message": '"todo_id" は必須項目です'}),
            }

        todo_table.delete_item(Key={"todo_id": todo_id})

        return {
            "statusCode": 204,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({}),
        }
    except Exception as e:
        print(f"Error deleting todo: {e}")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": "サーバーの内部でエラーが発生しました"}),
        }
