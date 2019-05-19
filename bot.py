
#################################################
### THIS FILE WAS AUTOGENERATED! DO NOT EDIT! ###
#################################################
# file to edit: dev_nb/bot.ipynb

from telegram.ext import Updater, InlineQueryHandler, CommandHandler
import pandas as pd
import requests
import re
import lib
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
"""

api_token = lib.config['telegram']['api_token']

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

class HenryBot:
    def __init__(self):
        self.db_conn = lib.DatabaseIO()
        self.triggers = self.db_conn.read_data('triggers')

    @staticmethod
    def start(update, context):
        """Send a message when the command /start is issued."""
        update.message.reply_text('Hi! I am HenryBot and you\'ve triggered me. You can add new triggers using /add. Get more information using /help')

    def update_triggers(self):
        self.db_conn.write_data(self.triggers, 'triggers')

    def add(self, update, context):
        try:
            value = update.messagetext.split(' ', 1)[1]
            trigger, response = map(strip, value.split(':', 1))
            self.triggers.loc[trigger] = [response]
            self.update_triggers()
            update.message.reply_text(f'\'{trigger}\' added to the triggers')
        except IndexError:
            update.message.reply_text(f"No correctly formatted trigger found. Add a new trigger by typing /add <trigger>:<response>!")

    def delete(self, update, context):
        try:
            trigger = update.message.text.split(' ', 1)[1]
            self.triggers = self.triggers.drop(trigger)
            self.update_triggers()
            update.message.reply_text(f'\'{trigger}\' deleted from triggers.')

        except IndexError:
            update.message.reply_text(f'Please add a trigger to remove. Format is /delete <trigger>')

    def get_triggers(self, update, context):
        message = ''
        update.message.reply_text('\n'.join(self.triggers.index.tolist()))
#         for trigger, row in self.triggers.iterrows():
#             message += f'{trigger}: {row.response}\n'
#         update.message.reply_text(message)

    def triggered(self, update, context):
        """Echo the user message."""
        text = update.message.text
        user = update.message.from_user
        message = ''

        # Respond to 'I am'
        matches = re.search(r'ik ben (\w+)', text, re.I)
        if matches is not None:
            message += f'Hoi {matches.group(1)}, ik ben HenryBot\n'

        # Respond to added triggers
        for trigger, row in self.triggers.iterrows():
            response = row['response']
            regex = r'\b' + trigger + r'\b|\A' + trigger + r'\b '
            if re.search(regex, text, re.I):
                message += self.triggers.loc[trigger, 'response'] + '\n'

        message = message.format(user=user.first_name)
        if message:
            update.message.reply_text(message)

    @staticmethod
    def help(update, context):
        """Send a message when the command /help is issued."""
        update.message.reply_text('Help!')


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    henry_bot = HenryBot()
    updater = Updater(api_token, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", henry_bot.start))
    dp.add_handler(CommandHandler("add", henry_bot.add))
    dp.add_handler(CommandHandler("delete", henry_bot.delete))
    dp.add_handler(CommandHandler("triggers", henry_bot.get_triggers))
    dp.add_handler(CommandHandler("help", henry_bot.help))

    # on noncommand i.e message - respond appropriately to the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, henry_bot.triggered))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
