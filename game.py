from player import Player


class Game:

    def __init__(self):
        self.players = dict()

    def addResult(self, player, points):
        self.players[player] = points

    def getMatchScores(self):
        scores = ""
        i = 1
        for player, points in sorted(self.players.items(), reverse=True):
            scores += "{}: {} - {}\n".format(i, player, points)
            i += 1
        return scores

    def getResults(self):
        players = []
        for player, points in self.players.items():
            players.append(Player(player, 1000, 0, points, 0))
        return players
