class TaskRunner:
    async def run(self, task_name: str, payload: dict) -> dict:
        raise NotImplementedError

