import os
import time
from slackclient import SlackClient


# starterbot's ID as an environment variable
BOT_ID = os.environ.get("BOT_ID")

# constants
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMAND = 'do '

# Add new word and corresponding reaction you want tsg_bot to use for tag
WORD_DICT = {'cancer':'ebola', 'ebola':'ebola', 'teemo':'ebola'}

# instantiate Slack & Twilio clients
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
turtleEvent = 'the third day of the Group Stage at MSI 2017 (TSM vs WE). '
turtleLink = 'https://clips.twitch.tv/HonestFunLorisCoolCat'

def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    response = "Not sure what you mean. Use the *" + EXAMPLE_COMMAND + \
               "* command."
    if command.startswith(EXAMPLE_COMMAND):
        response = "do it yourself"
    elif ('turtle' in command.lower()):
        response = 'The last time WildTurtle died while attempting to 1v5 was during ' \
                   + turtleEvent + turtleLink
    slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)


def add_reax(command, channel, timestamp, type):
    slack_client.api_call("reactions.add", name=WORD_DICT[type], channel=channel, timestamp=timestamp, as_user=True)


def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output:
                if AT_BOT in output['text']:
                    # return text after the @ mention, whitespace removed
                    return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel'], 'command', None
                for word in WORD_DICT.keys():
                    if word in output['text']:
                        return output['text'], output['channel'], word, output['ts']
    return None, None, None, None


if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
        while True:
            command, channel, type, timestamp = parse_slack_output(slack_client.rtm_read())
            if command and channel and type == 'command':
                handle_command(command, channel)
            elif command and channel and timestamp:
                add_reax(command, channel, timestamp, type)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
