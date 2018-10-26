from elo_scoring import ELOScoring
from player import Player
from string import Template
import os
import psycopg2
from psycopg2 import sql


class League:
    DATABASE_URL = os.environ['DATABASE_URL']

    conn = psycopg2.connect(DATABASE_URL, sslmode='require')

    leaderboard = []
    scoring = ELOScoring(32, 400)

    cursor = conn.cursor()

    # Create table
    cursor.execute('''CREATE TABLE IF NOT EXISTS ladder
                 (name TEXT UNIQUE, elo INT, position INT, points INT, games_played INT)''')
    cursor.execute('SELECT * FROM ladder ORDER BY position')
    for i in range(cursor.rowcount):
        row = cursor.fetchone()
        leaderboard.append(Player(row[0], row[1], row[2], row[3], row[4]))

    def getLeaderBoard(self):
        leaderboard = ""
        for player in sorted(self.leaderboard, key=Player.get_elo, reverse=True):
            leaderboard += ("Position: {}, Name: {}, ELO: {}\n".format(player.position, player.name, player.elo))

        if not leaderboard:
            return "There isn't currently a leaderboard!"

        return leaderboard

    def getLeaderBoardFormatted(self):
        t = Template(
            '{"title": "${position}", "fields": [{"title": "Name","value": "${name}","short": true},{"title": "ELO", '
            '"value": "${score}", "short": true}]}')
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
            self.cursor.execute(sql.SQL("INSERT INTO ladder (name, elo, position, points, games_played)"
                                        " VALUES ('{0}', {1}, {2}, {3}, {4}) ON CONFLICT(name) DO UPDATE "
                                        "SET elo={5}, position={6},  points={7}, games_played={8}".format(player.name,
                                        int(player.elo), int(player.position), int(player.points), int(player.games_played),
                                        int(player.elo), int(player.position), int(player.points), int(player.games_played))))

        # Save (commit) the changes
        self.conn.commit()

    def deleteTable(self):
        self.cursor.execute("DROP TABLE IF EXISTS ladder")
        return "Deleted the ladder."

    def predict(self, game):
        return self.scoring.predictScores(game, self.leaderboard)
