from celery import Celery
def test_a():
    celery = Celery('tasks', broker='amqp://guest:guest@localhost:5672//')
    print('d')


from celery.result import AsyncResult


def get_task_result(task_id):
    result = AsyncResult(task_id)

    # Check the task's status
    if result.state == 'PENDING':
        return {"status": "Task is still pending"}
    elif result.state == 'STARTED':
        return {"status": "Task is currently running"}
    elif result.state == 'SUCCESS':
        return {"status": "Task completed successfully", "result": result.result}
    elif result.state == 'FAILURE':
        return {"status": "Task failed", "error": str(result.result)}
    else:
        return {"status": f"Task state: {result.state}"}


if __name__ == '__main__':
    get_task_result("05b65ecd-de02-4f71-be3c-76af7924f073")