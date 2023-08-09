from fastapi import APIRouter, status
from fastapi.responses import Response

from summer_practice.tasks.schemas import Task, TaskStatus, TaskAdditional
from summer_practice.tasks.scheduler import app as app_rocketry
from summer_practice.tasks.utils import get_task_or_raise_http_except

session = app_rocketry.session

# Task
# ----
router_task = APIRouter(prefix="/tasks", tags=["task"])


@router_task.get('/info/{task_name}', response_model=Task)
async def task_info(task_name: str):
    task = get_task_or_raise_http_except(session=session, task_name=task_name)
    return Task(
        name=task.name,
        description=' '.join(task.description.split()) if task.description is not None else '',
        # Делаю так для нормализации пробелов в выводе
        period=str(task.period) + ' ' + str(task.start_cond.period),
        status=str(task.status),
        is_running=task.is_running,
        disabled=task.disabled,
        additional=TaskAdditional(**task.dict())
    )


@router_task.get('/list/', response_model=list[Task])
async def tasks_list():
    tasks = [
        Task(
            name=task.name,
            description=' '.join(task.description.split()) if task.description is not None else '',
            # Делаю так для нормализации пробелов в выводе
            period=str(task.period) + ' ' + str(task.start_cond.period),
            status=str(task.status),
            is_running=task.is_running,
            disabled=task.disabled,
            additional=TaskAdditional(**task.dict())
        )
        for task in session.tasks
    ]
    return tasks


@router_task.get("/status/{task_name}", response_model=TaskStatus)
async def task_status(task_name: str):
    task = get_task_or_raise_http_except(session=session, task_name=task_name)

    return TaskStatus(name=task.name, status=not task.disabled)


@router_task.post("/enable/{task_name}")
async def task_enable(task_name: str):
    task = get_task_or_raise_http_except(session=session, task_name=task_name)

    task.disabled = False
    return Response(status_code=status.HTTP_200_OK,
                    content=f"Задача '{task.name}' запущена! "
                            f"Периодичность выполнения: {str(task.period) + ' ' + str(task.start_cond.period)}.")


@router_task.post("/disable/{task_name}")
async def task_disable(task_name: str):
    task = get_task_or_raise_http_except(session=session, task_name=task_name)

    task.disabled = True
    return Response(status_code=status.HTTP_200_OK,
                    content="Парсер выключен.")


@router_task.post("/run/{task_name}")
async def task_run(task_name: str):
    task = get_task_or_raise_http_except(session=session, task_name=task_name)

    task.force_run = True
    return Response(status_code=status.HTTP_200_OK,
                    content="Задача принудительно запущена. По завершению, данные обновятся.")


@router_task.post("/terminate/{task_name}")
async def terminate_parser_task(task_name: str):
    task = get_task_or_raise_http_except(session=session, task_name=task_name)

    task.terminate()
    return Response(status_code=status.HTTP_200_OK,
                    content="Задача принудительно остановлена. Вероятно, данные были обработаны не полностью.")


@router_task.get("/logs/")
async def read_logs():
    """Get task logs"""
    repo = session.get_repo()
    return repo.filter_by().all()

# @router_task.get("/update_proxies", tags=["proxies"], name="Обновить HTTPS прокси")
# async def update_proxy():
#     await do_proxy_processes()
#
#     return {"detail": {"status": 200, "msg": "", "total_proxies": proxies_count}}
