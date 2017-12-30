import time
import re
from slackclient import SlackClient

from game import Game
from league import League

# instantiate Slack client
slack_client = SlackClient("your-token-here")
# starterbot's user ID in Slack: value is assigned after the bot starts up
starterbot_id = None

# constants
RTM_READ_DELAY = 1  # 1 second delay between reading from RTM
COMMAND_LIST = ("leaderboard", "match")
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
                return message, event["channel"]
    return None, None


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
        round.addResult(params[i].title(), params[i+1])

    league.recordGame(round)
    print(round.getMatchScores())
    return round.getMatchScores()


def handle_command(command, channel):
    """
        Executes bot command if the command is known
    """
    # Default response is help text for the user
    default_response = "Not sure what you mean. Try *{}*.".format(', '.join(COMMAND_LIST))

    # Finds and executes the given command, filling in response
    response = None
    # This is where you start to implement more commands!
    if command[0].lower() == COMMAND_LIST[0]:
        response = league.getLeaderBoard()
    elif command[0].lower() == COMMAND_LIST[1]:
        response = match(command[1:])

    # Sends the response back to the channel
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=response or default_response
    )


if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("Starter Bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            command, channel = parse_bot_commands(slack_client.rtm_read())
            if command:
                handle_command(command.split(), channel)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")