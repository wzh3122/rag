from app.tasks.base import TaskRunner


class IndexTaskRunner(TaskRunner):
    async def run(self, task_name: str, payload: dict) -> dict:
        return {"status": "reserved", "task_name": task_name, "payload_keys": list(payload.keys())}

