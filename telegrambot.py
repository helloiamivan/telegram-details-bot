#!/usr/bin/env python

from telegram import ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)
import csv
import logging
import os

# API Settings here
#TOKEN = "484913993:AAHjgjsdU_ofKC1lx6lnMXc4GXYn-KJkChI"
localFilePath = "C:\\Users\\1\\Desktop\\telegramDetails.csv"
#localFilePath = "/Users/ivanchan/Desktop/telegramDetails.csv"

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

TWITTER_REQUEST, EMAIL_REQUEST, ETH_REQUEST, CHECK_INPUT, SUBMIT = range(5)

reply_keyboard_submit_details = [['Submit Details'],['Cancel']]

reply_keyboard_check_details = [['Confirm Submission'],['Go Back']]

markup_submit_details = ReplyKeyboardMarkup(reply_keyboard_submit_details, one_time_keyboard=True)
markup_check_details = ReplyKeyboardMarkup(reply_keyboard_check_details, one_time_keyboard=True)

def facts_to_str(user_data):
    facts = list()

    for key, value in user_data.items():
        facts.append('{} - {}'.format(key, value))

    return "\n".join(facts).join(['\n', '\n'])

def start(bot, update):
    user = update.message.from_user
    update.message.reply_text(
    "Hello " + user.first_name + "."
    " I am your friendly SuperBitcoin bot."
    " Please fill in some details to claim your bounty."
    " Multiple submissions with the same telegram handle will be ignored."
    " Type /cancel at any point to exit",
        reply_markup=markup_submit_details)

    # If user don't have a valid telegram handle, end the conversation
    if user.username == None:
      update.message.reply_text("You do not have a valid Telegram ID! Please set your Telegram ID before submitting your details.")
      return ConversationHandler.END

    return TWITTER_REQUEST

def twitter_choice(bot, update, user_data):
    choice = update.message.text
    if choice == 'Cancel':
        user = update.message.from_user
        update.message.reply_text('Bye ' + user.first_name + '! Your details are not logged. I hope we can speak again some day.')
        return ConversationHandler.END

    elif choice == 'Submit Details':
        update.message.reply_text(
            'Please input in your Twitter ID with an "@". (Enter "NIL" if you have no Twitter ID)')
        return EMAIL_REQUEST

def email_choice(bot, update, user_data):
    text = update.message.text
    user_data['Twitter'] = text
    update.message.reply_text(
        'Please input your email for us to contact you on the forked bitcoin lucky draw. (Enter "NIL" if you have no email)')
    return ETH_REQUEST

    # if ("@" in text and "." in text) or (text == 'NIL'):
    #   user_data['Email Address'] = text
    #   return ETH_REQUEST

    # else:
    #   update.message.reply_text("Please check your email! Format should be xxxxx@xxxx.com")
    #   return EMAIL_REQUEST

def eth_choice(bot, update, user_data):
    text = update.message.text
    user_data['Email Address'] = text
    update.message.reply_text(
        'Please input your Ethereum address (Format should be 0x + 40 character hexadecimal).')
    return CHECK_INPUT

    # if ("@" in text and "." in text) or (text == 'NIL') or (text == 'nil') or (text == ('Nil')):
    #   user_data['Ethereum Address'] = text
    #   return SUBMIT
      
    # else:
    #   update.message.reply_text("Please check your Ethereum address! Format should be a 40 character hexadecimal")
    #   return ETH_REQUEST
def check_input(bot, update, user_data):
    text = update.message.text
    user_data['Ethereum Address'] = text
    update.message.reply_text("Please check the following details carefully before submitting:"
                            "{}".format(facts_to_str(user_data)), reply_markup=markup_check_details)
    return SUBMIT

def done(bot, update, user_data):
    selection = update.message.text

    if selection == 'Go Back':
        update.message.reply_text("Your details are not submitted. Type /start again to restart the submission")
        return ConversationHandler.END

    fields = ['','','','']

    # Grab telegram handle
    user = update.message.from_user
    fields[1] = user.username

    for key in user_data:

      if key == 'Twitter':
        fields[0] = user_data[key]

      elif key == 'Email Address':
        fields[2] = user_data[key]

      elif key == 'Ethereum Address':
        fields[3] = user_data[key]

    # Save details to a local CSV file
    if (fields[1] != None) and (fields[1] != ''):
      file = open(localFilePath,'a',newline='')
      writer = csv.writer(file)
      writer.writerow(fields)
      file.close()

      update.message.reply_text("Thank you for submitting your details, the following details have been logged:"
                                "{}".format(facts_to_str(user_data)))
      logger.info(user.username + ' has been successfully registered!')
      user_data.clear()

    return ConversationHandler.END

def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)

def cancel(bot, update):
    user = update.message.from_user
    update.message.reply_text('Bye ' + user.first_name + '! Your details are not logged. I hope we can speak again some day.')

    return ConversationHandler.END

def main():

    # Add conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            TWITTER_REQUEST: [MessageHandler(Filters.text,
                                           twitter_choice,
                                    pass_user_data=True),
                       ],

            EMAIL_REQUEST: [MessageHandler(Filters.text,
                                           email_choice,
                                    pass_user_data=True),
                       ],

            ETH_REQUEST: [MessageHandler(Filters.text,
                                           eth_choice,
                                    pass_user_data=True),
                       ],

            CHECK_INPUT:[MessageHandler(Filters.text,
                                           check_input,
                                    pass_user_data=True),
                       ],
                           
            SUBMIT: [MessageHandler(Filters.text,
                                          done,
                                          pass_user_data=True),
                       ]                                     
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    # Create the Updater
    PORT = int(os.environ.get('PORT', '8443'))
    TOKEN = "490230105:AAE-qtQ3Db8fyx_i3McE9_hiezQAE3hKl1E"
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher
    
    dp.add_handler(conv_handler)

    # log all errors
    dp.add_error_handler(error)

    # Start bot
    updater.start_webhook(listen="0.0.0.0",
                          port=PORT,
                          url_path=TOKEN)
    updater.bot.set_webhook("https://telegram-details-bot.herokuapp.com/" + TOKEN)
    updater.idle()

if __name__ == '__main__':
    print("Bot is running... Press Ctrl + C to end it")
    main()
