import os
import re
import requests

from random import randint

from telegram import Bot, Update, MessageEntity, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import MessageHandler, Filters, CommandHandler, BaseFilter
from telegram.error import BadRequest
from dynamic_preferences.registries import global_preferences_registry

from telebaka_robot.models import PermittedRobotUser


global_preferences = global_preferences_registry.manager()


def is_permitted(chat_id):
    return PermittedRobotUser.objects.filter(user_id=chat_id).exists()


def roll(bot: Bot, update: Update):
    argv = update.message.text.split(' ')
    start = 0
    end = 100

    try:
        if len(argv) == 2:
            end = int(argv[1])
        elif len(argv) == 3:
            start = int(argv[1])
            end = int(argv[2])

        if end < start:
            raise ValueError
    except ValueError:
        return

    update.message.reply_text(str(randint(start, end)))


def save_file(bot: Bot, update: Update):
    if not is_permitted(update.message.chat_id):
        return update.message.reply_text('Go away')

    markup = InlineKeyboardMarkup([])

    if update.message.photo:
        file_id = update.message.photo[-1].file_id
    elif update.message.audio:
        file_id = update.message.audio.file_id
    elif update.message.video:
        file_id = update.message.video.file_id
    elif update.message.document:
        file_id = update.message.document.file_id
    else:
        return

    file = bot.get_file(file_id)
    filename = os.path.basename(file.file_path)
    file.download(os.path.join(global_preferences['robot__upload_directory'], filename))
    file_url = global_preferences["robot__link_template"].format(filename)
    if update.message.photo:
        markup.inline_keyboard = [[
            InlineKeyboardButton('Google Image Search', f'https://www.google.com/searchbyimage?image_url={file_url}'),
            InlineKeyboardButton('SauceNao', f'https://saucenao.com/search.php?url={file_url}')
        ]]
    update.message.reply_text(file_url, disable_web_page_preview=True, reply_markup=markup)


def document_downloader(bot: Bot, update: Update):
    if not is_permitted(update.message.chat_id):
        return update.message.reply_text('Go away')

    links = update.message.parse_entities('url').values()
    for link in links:
        try:
            twitter_matches = re.match(r'https?://twitter.com/[A-Za-z0-9_]{1,15}/status/(\d+).*', link)
            if link.endswith('.gif'):
                update.message.reply_document(link)
            elif twitter_matches:
                r = requests.get(
                    'https://api.twitter.com/1.1/statuses/show.json', {'id': twitter_matches.group(1)},
                    headers={'Authorization': 'Bearer {}'.format(global_preferences['robot__twitter_api_token'])}
                )
                if r.status_code != 200:
                    return update.message.reply_text('Tweet is not found')
                tweet_info = r.json()
                try:
                    for media in tweet_info['extended_entities']['media']:
                        if media['type'] == 'video':
                            max_bitrate = -1
                            max_bitrate_link = None
                            for variant in media['video_info']['variants']:
                                if variant['content_type'] == 'video/mp4' and variant['bitrate'] > max_bitrate:
                                    max_bitrate = variant['bitrate']
                                    max_bitrate_link = variant['url']
                            if max_bitrate_link is not None:
                                update.message.reply_video(max_bitrate_link)
                except KeyError:
                    update.message.reply_text('Unable to retrieve video info from tweet')
            else:
                update.message.reply_text('Can\'t detect link type')
        except BadRequest:
            update.message.reply_text('Unable to retrieve file')


def trigger_exception(bot: Bot, update: Update):
    update.message.reply_text('Triggering exception...')
    raise Exception('Test exception')


def setup(dispatcher):
    dispatcher.add_handler(CommandHandler('roll', roll))
    dispatcher.add_handler(CommandHandler('exception', trigger_exception))
    dispatcher.add_handler(MessageHandler(Filters.audio | Filters.photo | Filters.video | Filters.document, save_file))
    dispatcher.add_handler(MessageHandler(Filters.text & (Filters.entity(MessageEntity.URL) |
                                          Filters.entity(MessageEntity.TEXT_LINK)), document_downloader))
    return dispatcher
