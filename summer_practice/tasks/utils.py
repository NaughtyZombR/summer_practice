from fastapi import HTTPException, status
from rocketry import Session
from rocketry.core import Task


def get_task_or_raise_http_except(session: Session, task_name) -> Task:
    task = session[task_name] if session.__contains__(task_name) else None

    if task is None:
        content = "Переданное имя задачи не соответствует имеющимся. Перепроверьте правильность ввода."
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=content)

    return task
