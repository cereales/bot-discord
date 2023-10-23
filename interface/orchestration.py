from utils import tools
import logging
logger = logging.getLogger(__name__)
logger_thread = logging.getLogger("thread_verbose")
logger_thread.setLevel(logging.ERROR)

import threading, asyncio
from asyncio.exceptions import CancelledError
from enum import Enum, auto
from discord.ext import commands
from game import pendu # to be able to reference pendu
from game.pendu import view, controller
from interface.bot import DiscordBot
from mvc.ui import DiscordUI
from utils.language import MessageNLS
from utils.language_resources.MessageLiterals import MessageLiterals


class OrchestratorType(Enum):
    DISCORD = auto()

class Orchestrator:
    """
    Main orchestrator.
    """
    def __init__(self, config_path, config_context):
        self.terminate = False
        self.listeners = []
        self.listeners.append(DiscordOrchestrator(self, config_path, config_context))

    def run(self):
        """
        Start listening of declared channels.

        In case of Ctrl+C, asyncio.run is expected to catch KeyboardInterrupt.
        Others asyncio method will deal with CancelledError.

        In case of clean close (from command), we will raise of own
        KeyboardInterrupt exception to others.
        """
        try:
            asyncio.run(self.gather_listeners())
        except KeyboardInterrupt:
            logger.warning("Ctrl+C catched.")
            for orchestrator in self.listeners:
                asyncio.run(orchestrator.close())

    async def gather_listeners(self):
        """
        In case of close command, a KeyboardInterrupt is raised from wait_for_end.
        """
        logger.log(tools.Constant.VERBOSE, "Start all listeners.")
        try:
            await asyncio.gather(*[orchestrator.start() for orchestrator in self.listeners], self.wait_for_end())
        except KeyboardInterrupt:
            # Do not do anything here because KeyboardInterrupt is forwarded to all asyncio methods.
            # try/catch in order to consume exception.
            pass

    async def close(self):
        self.terminate = True

    async def wait_for_end(self):
        while not self.terminate:
            await asyncio.sleep(1)
        logger.debug("Detected stop instruction.")
        raise KeyboardInterrupt()


class DiscordOrchestrator(DiscordBot):
    """
    Orchestrator dedicated to listening to discord events.

    For implementation limitation reasons, there are commands, gathered into
    groups called Cog.
    These Cogs are registered at login.

    This instance is connected with a bot account, and will forward events to
    appropriate views.
    Views must be registered with open_new_view().
    For now, only 1 view can be open per channel.
    """
    def __init__(self, main_orchestrator, config_path, config_context):
        logger.log(tools.Constant.VERBOSE, "__init__(%s, %s)", config_path, config_context)
        super().__init__(config_path, config_context)
        self.all_views = dict() # map channel_id to the view object
        self.main_orchestrator = main_orchestrator

    async def setup_hook(self):
        """
        Setup bot. Only called once in login().
        """
        await self.add_cog(Games(self))
        await self.add_cog(Admin(self))

    async def on_ready(self):
        await super().on_ready()

    async def close_all(self):
        """
        Forward close instruction to the main orchestrator.
        """
        await self.main_orchestrator.close()

    # Views management

    def can_open_new_view(self, channel_id):
        """
        Return True if the provided channel id is available for a new view.
        False otherwise.
        """
        return channel_id not in self.all_views

    def lock_new_view(self, channel_id):
        """
        Lock the channel id to prevent from initialising multiple views,
        due to asynchronism.
        The channel id must be available.

        @param  channel_id  The channel id must be available.
        @raise  AssertionError  If the channel is not available.
        """
        assert self.can_open_new_view(channel_id)
        self.all_views[channel_id] = None

    def open_new_view(self, channel_id, view):
        """
        Register the view with its associated channel id.
        The channel id must be locked.

        @raise  AssertionError  If the channel id is not locked.
        """
        assert channel_id in self.all_views, "Channel must be previously locked."
        assert self.all_views[channel_id] is None, "Channel is already open."
        self.all_views[channel_id] = view

    def close_view(self, channel_id):
        """
        Unregister the channel id.
        Events for this channel id will not be forward anymore.
        """
        self.all_views.pop(channel_id)

    # Event forwarding

    async def on_message(self, message):
        """
        Forward on_message event.
        """
        await super().on_message(message)
        if message.channel.id in self.all_views:
            await self.all_views[message.channel.id].on_message(message)

class Admin(commands.Cog, name="Administration"):
    """
    Admin commands.
    """
    def __init__(self, bot):
        self.bot = bot

    async def cog_before_invoke(self, ctx):
        """
        Executed before every command in this Admin Cog.
        Checks for admin permission from config.
        """
        if not self.bot.is_admin(ctx.author.id):
            raise commands.errors.CheckFailure()
        logger.debug("%s is an admin.", ctx.author.display_name)

    @commands.command(name='stop')
    async def stop(self, ctx):
        """
        Disconnect the bot.
        """
        await self.bot.close_all()

class Games(commands.Cog, name="Jeux"):
    """
    Tous les jeux disponibles. 1 seul jeu en cours par salon.
    All available games. Only 1 game per channel.
    """
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator    # Works as if it is the same class

    @commands.command(name="pendu")
    async def init_pendu(self, ctx):
        """
        Devine le mot caché.
        Guess the hidden word.
        """
        if not self.orchestrator.can_open_new_view(ctx.channel.id):
            pass
        else:
            self.orchestrator.lock_new_view(ctx.channel.id)
            view = pendu.view.View(DiscordUI(ctx.channel))
            controller = pendu.controller.Controller(self.orchestrator, ctx, view)
            self.orchestrator.open_new_view(ctx.channel.id, view)
            await controller.loop()
