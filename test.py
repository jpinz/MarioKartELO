from game import Game
from league import League
from player import Player
from elo_scoring import ELOScoring



league = League()

round1 = Game()

round1.addResult("Julian", 53)
round1.addResult("Bag", 54)
round1.addResult("Tim", 58)
round1.addResult("Res", 60)

print(round1.getMatchScores())


league.recordGame(round1)

round2 = Game()


round2.addResult("Julian", 56)
round2.addResult("Res", 59)
round2.addResult("Tim", 59)
round2.addResult("Bag", 57)
print(round2.getMatchScores())

league.recordGame(round2)

print(league.getLeaderBoard())
