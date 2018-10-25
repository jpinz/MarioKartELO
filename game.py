from player import Player
from string import Template

class Game:

    def __init__(self):
        self.players = dict()

    def addResult(self, player, points):
        print(player)
        self.players[player] = points

    def getMatchScores(self):
        scores = ""
        i = 1
        print(self.players)
        for player, points in sorted(self.players.items(), reverse=True):
            scores += "{}: {} - {}\n".format(i, player, points)
            i += 1
        return scores

    def getMatchScoresFormatted(self):

        t = Template('{"title": "${name}", "fields": [{"title": "Position","value": "${position}","short": true},{"title": "Score", "value": "${score}", "short": true}]')
        scores = '['
        i = 1
        length = len(self.players.items())
        for player, points in sorted(self.players.items(), key=lambda value: value[1], reverse=True):

            scores += t.substitute(name = player, position = i, score = points)
            scores += '}'
            if i != length:
                scores += ','
            i += 1

        scores += ']'
        return scores

    def getResults(self):
        players = []
        for player, points in self.players.items():
            players.append(Player(player, 1000, 0, points, 0))
        return players
