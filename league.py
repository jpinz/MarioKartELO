from elo_scoring import ELOScoring
from player import Player
import sqlite3


class League:
    leaderboard = []
    scoring = ELOScoring(16, 480)

    conn = sqlite3.connect('ladder.db')
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
