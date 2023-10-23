from utils import tools
import logging
logger = logging.getLogger(__name__)

import discord, configparser, traceback
from discord.ext import commands
from utils.language import MessageNLS
from utils.language_resources.MessageLiterals import MessageLiterals
from utils.tools import Constant


class DiscordBot(commands.Bot):
    """
    A bot class to be able to interact with discord API.
    """
    def __init__(self, config_path, config_context):
        logger.log(tools.Constant.VERBOSE, "__init__(%s, %s)", config_path, config_context)
        self.read_config(config_path, config_context)
        super().__init__(command_prefix=self.command_prefix, intents=discord.Intents.all())
        self.error_count = 0

    # config init

    def read_config(self, config_path, profil_section):
        """
        Initialise bot with settings from configuration file.
        """
        try:
            config = configparser.ConfigParser(default_section="DEFAULT",
                    inline_comment_prefixes=('#'), # to enable comments in lines
                    allow_no_value=True,
                    empty_lines_in_values=False)
            config.read(config_path)

            # Mandatory attributes
            self.command_prefix = config.get(profil_section, "prefix_command")
            self.token = config.get(profil_section, "token")

            # Optional attributes
            self.error_channel = config.getint(profil_section, "error_channel", fallback=None)
            self.target_channel = config.getint(profil_section, "target_channel", fallback=None)

            # Admins section
            self.admins = set()
            admins = config["ADMINS"]
            for admin_id, no_value in admins.items():
                if no_value is None:
                    try:
                        admin = int(admin_id)
                        self.admins.add(admin)
                    except ValueError:
                        logger.warning("Non expected non-integer value in ADMINDS section.")
        except:
            logger.error("Cannot read properly config file.")
            raise

    # bot connection

    def run(self, *args, **kwargs):
        if Constant.NO_INTERNET:
            logger.error("Internet set to : OFF")
        else:
            super().run(self.token, *args, **kwargs)

    async def start(self, *args, **kwargs):
        """
        To be called without token.
        super signature is with token in parameters.
        By calling with token, it will be integrated in args and then ignored.
        """
        if Constant.NO_INTERNET:
            logger.error("Internet set to : OFF")
        else:
            await super().start(self.token, **kwargs)

    async def close(self):
        """
        Called when KeyboardInterrupt is catched by asyncio.
        """
        if self.is_closed():
            logger.debug("%s already disconected.", self.user.name)
        else:
            logger.warning("Close requested.")
            await super().close()
            logger.info("%s is now disconected.", self.user.name)
            if self.error_count > 0:
                logger.error("%s errors occured during session.", self.error_count)

    async def on_ready(self):
        """
        Set help message as activity.
        Initialise channels.
        """
        # Set channels
        if self.error_channel is not None:
            try:
                self.error_channel = self.get_channel(self.error_channel)
            except:
                self.error_channel = None
                logger.exception("Fail to get channel for error logs.")
        if self.target_channel is not None:
            try:
                self.target_channel = self.get_channel(self.target_channel)
            except:
                self.target_channel = None
                logger.exception("Fail to get target_channel.")

        # Set help message
        helpMessage = discord.Game(self.command_prefix + "help for help")
        await self.change_presence(activity=helpMessage)

        logger.info("%s has connected to Discord!", self.user.name)

    # bot events

    async def on_message(self, message, do_not_log=False):
        """
        When this method is overriden, it should call at the beginning with
        `super().on_message(message)`
        """
        if not do_not_log:
            self.log_input_message(message)
        await super().on_message(message)

    def log_input_message(self, message):
        if logger.isEnabledFor(Constant.VERBOSE):
            UNKNOWN = "unknown"
            context = None
            if isinstance(message.channel, discord.DMChannel):
                if message.channel.recipient is not None:
                    context = "PRIV/" + message.channel.recipient.display_name
            elif isinstance(message.channel, discord.GroupChannel):
                if message.channel.name is not None:
                    context = "PRIV/" + message.channel.name
                else:
                    context = "GROUP/<" + str(len(message.channel.recipients)) + " pers.>"
            elif isinstance(message.channel, discord.TextChannel):
                context = message.channel.guild.name
                if message.channel.category is not None:
                    context += "/" + message.channel.category.name
                context += "/" + message.channel.name
            else:
                context = UNKNOWN
            logger.log(Constant.VERBOSE, "(%s <%s>) [%s <%s>] %s:%s%s",
                    context, message.channel.id,
                    message.author.display_name, message.author.id,
                    message.id,
                    '\n' if '\n' in message.content else ' ', message.content)

    async def on_raw_reaction_add(self, payload):
        """
        When this method is overriden, it should call at the beginning with
        `super().on_raw_reaction_add(payload)`
        """
        logger.log(Constant.VERBOSE, "Reaction %s detected <%s>.".format(payload.emoji.name, payload.emoji.name.encode("ascii", 'backslashreplace')))
        await super().on_raw_reaction_add(payload)

    async def on_error(self, event, *args, **kwargs):
        self.error_count += 1
        logger.exception("Catched an error in %s:", event)
        if self.error_channel:
            await self.error_channel.send("```\n" + traceback.format_exc() + "\n```")

    async def on_command_error(self, ctx, error):
        """
        @param error    is of commands.CommandError type.
        """
        if isinstance(error, commands.errors.CommandNotFound):
            await super().on_command_error(ctx, error)
        elif isinstance(error, commands.errors.CheckFailure):
            await ctx.send(MessageNLS.get_message(MessageLiterals.INVALID_ROLE))
        else:
            # so that traceback is sent to error_channel
            raise error

    def is_admin(self, user_id):
        return user_id in self.admins
