# aws-sam-todo-api

## ローカル環境構築

DynamoDB の準備

```sh
docker compose up -d

aws dynamodb create-table \
  --table-name todos \
  --attribute-definitions AttributeName=todo_id,AttributeType=S \
  --key-schema AttributeName=todo_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --endpoint-url http://localhost:8000
```

Lambda の起動

```sh
sam build
sam local start-api --env-vars env.json --docker-network lambda-local
```
