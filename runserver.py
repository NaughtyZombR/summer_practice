"""
This file combines the two applications.
"""

import os
import sys

sys.path.append(os.path.abspath("./summer_practice"))

import asyncio
import logging

import uvicorn

from summer_practice.main import app as app_fastapi
from summer_practice.tasks.scheduler import app as app_rocketry


class Server(uvicorn.Server):
    """Customized uvicorn.Server

    Uvicorn server overrides signals and we need to include
    Rocketry to the signals."""

    def handle_exit(self, sig: int, frame) -> None:
        app_rocketry.session.shut_down()
        return super().handle_exit(sig, frame)


async def main():
    "Run Rocketry and FastAPI"

    server = Server(config=uvicorn.Config(app_fastapi, workers=1, log_level="debug", loop="asyncio",
                                          host="0.0.0.0", port=8080))

    api = asyncio.create_task(server.serve())
    sched = asyncio.create_task(app_rocketry.serve())

    await asyncio.wait([api, sched])


if __name__ == "__main__":
    # Print Rocketry's logs to terminal
    logger = logging.getLogger("rocketry.task")
    logger.addHandler(logging.StreamHandler())

    # Run both applications
    asyncio.run(main())
