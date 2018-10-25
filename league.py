from elo_scoring import ELOScoring
from player import Player
from string import Template
import os
import psycopg2

DATABASE_URL = os.environ['DATABASE_URL']

conn = psycopg2.connect(DATABASE_URL, sslmode='require')

class League:
    leaderboard = []
    scoring = ELOScoring(16, 480)

    c = conn.cursor()

    # Create table
    c.execute('''CREATE TABLE IF NOT EXISTS ladder
                 (name TEXT UNIQUE, elo INT, position INT, points INT, games_played INT)''')

    for row in c.execute('SELECT * FROM ladder ORDER BY position'):
        leaderboard.append(Player(row[0], row[1], row[2], row[3], row[4]))

    def getLeaderBoard(self):
        leaderboard = ""
        for player in sorted(self.leaderboard, key=Player.get_elo, reverse=True):
            leaderboard += ("Position: {}, Name: {}, ELO: {}\n".format(player.position, player.name, player.elo))
        return leaderboard

    def getLeaderBoardFormatted(self):
        t = Template(
            '{"title": "${position}", "fields": [{"title": "Name","value": "${name}","short": true},{"title": "ELO", "value": "${score}", "short": true}]}')
        leaderboard = '['
        i = 1
        length = len(self.leaderboard)
        for player in sorted(self.leaderboard, key=Player.get_elo, reverse=True):

            leaderboard += t.substitute(name=player.name, position=player.position, score=player.elo)
            if i != length:
                leaderboard += ','
            i += 1

        leaderboard += ']'
        return leaderboard

    def recordGame(self, game):
        self.leaderboard = self.scoring.updateScores(game, self.leaderboard)
        self.scoring.set_position(self.leaderboard)

        for player in self.leaderboard:
            # Insert a row of data
            if player in game.getResults():
                player.add_game()
            self.c.execute("INSERT OR REPLACE INTO ladder VALUES (?, ?, ?, ?, ?)",
                           [player.name, player.elo, player.position, player.points, player.games_played])

        # Save (commit) the changes
        self.conn.commit()
