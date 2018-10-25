from elo_scoring import ELOScoring
from player import Player
from string import Template
import sqlite3


class League:
    leaderboard = []
    scoring = ELOScoring(96, 480)

    conn = sqlite3.connect('ladder.db')
    cursor = conn.cursor()

    # Create table
    cursor.execute('''CREATE TABLE IF NOT EXISTS ladder
                 (name TEXT UNIQUE, elo INT, position INT, points INT, games_played INT)''')

    for row in cursor.execute('SELECT * FROM ladder ORDER BY position'):
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
            self.cursor.execute("INSERT OR REPLACE INTO ladder VALUES (?, ?, ?, ?, ?)",
                                [player.name, player.elo, player.position, player.points, player.games_played])

        # Save (commit) the changes
        self.conn.commit()

    def deleteTable(self):
        self.cursor.execute("DROP TABLE IF EXISTS ladder")
        return "Deleted the ladder."

    def predict(self, game):
        return self.scoring.predictScores(game, self.leaderboard)
