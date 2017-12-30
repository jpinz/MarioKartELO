from game import Game
from league import League
from player import Player
from elo_scoring import ELOScoring



league = League()

round1 = Game()

round1.addResult("P1", 53)
round1.addResult("P2", 54)
round1.addResult("P3", 58)
round1.addResult("P4", 60)

print(round1.getMatchScores())


league.recordGame(round1)

round2 = Game()


round2.addResult("P1", 56)
round2.addResult("P4", 59)
round2.addResult("P2", 59)
round2.addResult("P3", 57)
print(round2.getMatchScores())

league.recordGame(round2)

print(league.getLeaderBoard())
