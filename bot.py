#!/usr/bin/env python
# pylint: disable=unused-argument, wrong-import-position
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import json

###########################
# For serving resource list
from telegram import Update, ForceReply, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler, CallbackContext

from telegram import __version__ as TG_VER

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text(update.message.text)

################################################
# Resource list (keyword: file URL or file path)
resources = {
    "Bitcoin": {
        "file_url": "bitcoin.pdf"
    },
    "The Principles Of Tokenomics": {
        "file_url": "principles-of-tokenomics.pdf"
    },
    # Add more resources with their respective file URLs
}

# Define the /resources command handler
async def resources_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message containing the available resources with hyperlinks."""
    keyboard = [
        [InlineKeyboardButton(keyword, callback_data=keyword) for keyword in resources.keys()]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Resources:\n",
        reply_markup=reply_markup
    )

# Define the callback query handler to handle resource button clicks
from telegram import InputFile

async def handle_resource_button(update: Update, context: CallbackContext):
    query = update.callback_query
    resource_key = query.data

    if resource_key in resources:
        file_url = resources[resource_key]["file_url"]

        # Send the file back to the user
        with open(file_url, "rb") as file:
            await query.message.reply_document(document=InputFile(file))
    else:
        await query.message.reply_text("Resource not found.")

def main() -> None:
    """Start the bot."""
    # Load the token from config.json
    with open('config.json') as f:
        data = json.load(f)
    token = data['telegram_bot_token']

    # Create the Application and pass it your bot's token.
    application = Application.builder().token(token).build()

    # Add command handler for /resources command
    application.add_handler(CommandHandler("resources", resources_command))

    # Add callback query handler for resource buttons
    application.add_handler(CallbackQueryHandler(handle_resource_button))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()