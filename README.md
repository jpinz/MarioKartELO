# MarioKartELO
Slackbot to rank players in Mario Kart based on their points at the end of a grand prix.

# How to setup
Create a slackbot and paste the Bot ID Token in slackbot.py: 

`slack_client = SlackClient("your-token-here")`

Then just run slackbot.py

# How does it work?
The algorithm is the a normal ELO Algorithm except to make it multiplayer it evaluates each player in the game against every other player to calculate everyone's ELOs.

I'll refer to test.py to give the steps.

First we create a new League object, and then a game for the first round.

We add results to the first round/game with names of players and their score at the end of the grand prix. We also print the place each player came in based on their point values.

Then we record the game in the league.

We do the same thing again for a second game.

Then we finally print the leaderboard.

The leaderboard is stored in an sqlite db called ladder.db. It is created on the first run of making a league.

