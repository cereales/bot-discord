"""
This module defines what is a View.
One instance for each player.

On the player's turn, the controller calls `call` method with callback parameter.
And it is expecting the method to exit after calling callback with move to play.
"""
from utils import tools
import logging
logger = logging.getLogger(__name__)

from mvc.ui import AbstractUI


class AbstractView:
    """
    A view is connected to a single controller.

    The view must filter if this event is expected or not, and answer to the
    controller through the callback only when required.
    """
    def __init__(self, id):
        self.id = id

    async def call(self, callback):
        """
        Method called for one player turn.
        """
        raise NotImplementedError()


class UserInteractView(AbstractView):
    """
    This object is an interface with the player(s).
    It will wait for user interaction.

    It is called by the orchestrator when an event is received on the associated ui.
    Call is forwarded to the ui.
    """
    def __init__(self, ui: AbstractUI):
        assert isinstance(ui, AbstractUI) # python does not check type
        super().__init__(ui.id)
        self.ui = ui
        self.ui.view = self
        self.callback = None

    async def send(self, callback):
        """
        To be overriden.
        This method is called to ask a move to the player at the start of its turn.
        The implementation must define the behavior.
        """
        raise NotImplementedError()

    async def call(self, callback):
        """
        The controller calls this method at the start of the turn of the current player.
        """
        self.callback = callback
        await self.send(callback)

    async def on_message(self, message):
        """
        Orchestrator forwards messages here.
        On a detected move, submit letter to callback.
        """
        raise NotImplementedError()

    def is_expected_on_message(self, message):
        """
        Return True if the view is expecting an answer from the user.
        To be called on on_message event.
        """
        res = self.callback is not None
        if not res:
            logger.log(tools.Constant.VERBOSE, "Callback is None: Not expecting any message.")
        return res

    def get_callback(self):
        """
        Return the stored callback and remove it.
        A callback can be used only once. Retrieve only when ready to use.
        """
        callback = self.callback
        self.callback = None # callback is only used for one answer/turn
        return callback
