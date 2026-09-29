"""Persistence adapter. Uses in-memory storage locally and DynamoDB on AWS."""
from __future__ import annotations
import os
from datetime import datetime, timezone
import boto3

# TABLE_NAME is set in AWS. If absent, a process-local dictionary is used.
_TABLE_NAME = os.getenv("TABLE_NAME")
_memory: dict[str, dict] = {}
_table = boto3.resource("dynamodb").Table(_TABLE_NAME) if _TABLE_NAME else None

def put(item_id: str, item_type: str, value: dict) -> None:
    # Prefix keys by entity type so one DynamoDB table can store multiple record types.
    key = f"{item_type}#{item_id}"
    if _table is None:
        _memory[key] = value
        return
    _table.put_item(Item={"pk": key, "data": value, "updatedAt": datetime.now(timezone.utc).isoformat()})

def get(item_id: str, item_type: str) -> dict | None:
    # Keep the same interface for local memory and DynamoDB persistence.
    key = f"{item_type}#{item_id}"
    if _table is None:
        return _memory.get(key)
    out = _table.get_item(Key={"pk": key})
    return out.get("Item", {}).get("data")
