"""
This module defines what is a User Interface.
This manages the sending of informations.
It is used by the view when an event is received on the channel.
"""
from utils import tools
import logging
logger = logging.getLogger(__name__)


class AbstractUI:
    def __init__(self, id):
        self.id = id
        self.view = None    # init by the view itself.

    async def send(self, message):
        """
        Send the message on the ui.
        """
        raise NotImplementedError()

    def get_message(self, message):
        return message

    def get_message_id(self, message):
        return None


class ConsoleUI(AbstractUI):
    """
    This interface manage interactions through terminal.
    """
    def __init__(self):
        super().__init__("stdin")

    async def send(self, message):
        print(message)


class DiscordUI(AbstractUI):
    """
    This interface manage Discord interactions.
    """
    def __init__(self, channel):
        super().__init__(channel.id)
        self.channel = channel

    async def send(self, message):
        await self.channel.send(message)

    def get_message(self, message):
        return message.content

    def get_message_id(self, message):
        return message.id
