import time
import re
import json
from slackclient import SlackClient

from game import Game
# from league import League
from league_sqlite import League

# instantiate Slack client
# tkezm xoxb-32580638016-463335718673-Z4VqRPPcdYmrH86qwHQaITPh
# testing xoxb-292507756724-aROyaerbZPfCnwc3gbwjdPTj
slack_client = SlackClient("xoxb-292507756724-aROyaerbZPfCnwc3gbwjdPTj")
# starterbot's user ID in Slack: value is assigned after the bot starts up
starterbot_id = None

# constants
RTM_READ_DELAY = 1  # 1 second delay between reading from RTM
COMMAND_LIST = ("leaderboard", "match", "deletetable", "update", "undo", "predict")
MENTION_REGEX = "^<@(|[WU].+)>(.*)"

league = League()


def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == starterbot_id:
                return message, event["channel"], event["user"]
    return None, None, None


def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)


def match(params):
    round = Game()
    for i in range(0, len(params), 2):
        if int(params[i + 1]) > 60:
            return "Can't have more than 60 points for a game. Please either divide to get score out of 60, or take the" \
                   " score from every 4 games."
        round.addResult(params[i], params[i + 1])

    league.recordGame(round)
    return round.getMatchScores()


def predict(params):
    round = Game()
    for i in range(0, len(params)):
        round.addResult(params[i], -1)

    return league.predict(round)


def handle_command(command, channel, user):
    """
        Executes bot command if the command is known
    """
    # Default response is help text for the user
    default_response = "Not sure what you mean. Try *{}*.".format(', '.join(COMMAND_LIST))

    # Finds and executes the given command, filling in response
    response = None
    wantFormattedOutput = False
    text = "Title"
    # This is where you start to implement more commands!
    if command[0].lower() == COMMAND_LIST[0] or command[0][0].lower() == COMMAND_LIST[0][0]:
        response = league.getLeaderBoard()
        text = "Leaderboard"
    elif command[0].lower() == COMMAND_LIST[1] or command[0][0].lower() == COMMAND_LIST[1][0]:
        response = match(command[1:])
        text = "Match"
    elif command[0].lower() == COMMAND_LIST[2] and (user == "U4AAX9J0Y" or user == "U8LJ5709K"):
        response = league.deleteTable()
    # elif command[0].lower() == COMMAND_LIST[3]:
    #    response = "Not yet implemented - will eventually delete a user: " + command[1:]
    elif command[0].lower() == COMMAND_LIST[5] or command[0][0].lower() == COMMAND_LIST[5][0]:
        response = predict(command[1:])
        text = "Prediction"
    print(response)

    if wantFormattedOutput:
        if response:
            # Sends the response back to the channel
            slack_client.api_call(
                "chat.postMessage",
                channel=channel,
                text=text,
                attachments=json.loads(response))
        else:
            slack_client.api_call(
                "chat.postMessage",
                channel=channel,
                text=default_response)
    else:
        # Sends the response back to the channel
        slack_client.api_call(
            "chat.postMessage",
            channel=channel,
            text=response or default_response)


if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("Starter Bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            command, channel, user = parse_bot_commands(slack_client.rtm_read())
            print(user)
            if command:
                # if channel == "CDMTQ45V0":  # If mariokart channel on tkezm
                    handle_command(command.split(), channel, user)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")
