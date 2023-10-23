"""
This module defines what is a Controller.
"""
from utils import tools
import logging
logger = logging.getLogger(__name__)

import asyncio
from time import time


class AbstractController:
    """
    The Controller is responsible of the logic of the game.
    It calls views with callback and wait for the answer.
    """
    def __init__(self, orchestrator, model, main_view):
        self.model = model
        self.orchestrator = orchestrator
        self.main_view = main_view

    # Getters

    def get_main_view(self):
        return self.main_view

    # Lifecycle

    @staticmethod
    async def call(view, callback, timeout=None):
        """
        Call the view.

        @raise  TimeoutError    if no answer before timeout.
        @raise  Exception       if exception catched during call to view
        """
        await asyncio.gather(
                callback.wait(timeout=timeout),
                AbstractController.call_view_surrounder(view, callback))

    @staticmethod
    async def call_view_surrounder(view, callback):
        """
        Detects the end of view call to disable timeout.
        """
        await view.call(callback)
        callback.end_call = True


class AbstractCallback:
    """
    A Callback is given to a view, to let it interact with the controller.
    By using this interface, the integrity of controller is preserved.

    One Callback is created for each player turn.
    A Callback must contain all the input data for the view.
    `answered` variable must be set to True when the view play a move.
    """
    def __init__(self):
        self.end_call = False  # This is set to True when the call to view ends.

    def is_ready(self):
        """
        True when the view answered and terminated.
        """
        return self.end_call and self.answered()

    def answered(self):
        """
        Return True when a move has been provided.
        To be implemented by subclass.

        @return     Ture when all output data members are set. False otherwise.
        """
        raise NotImplementedError()

    async def wait(self, timeout=None):
        """
        Raise a TimeoutError if no move is provided before the timeout duration.

        @param  timeout     Timeout duration in seconds. None if no timeout requested.
        @raise  TimeoutError
        """
        start_time = time()
        await asyncio.sleep(.05)
        while not self.is_ready():
            if timeout is not None and time() - start_time > timeout:
                logger.log(tools.Constant.VERBOSE, "Raise timeout ! (%f/%ssec)", time() - start_time, timeout)
                raise TimeoutError()
            await asyncio.sleep(1)
        logger.log(tools.Constant.VERBOSE, "Answer in time : %f/%ssec", time() - start_time, timeout)
