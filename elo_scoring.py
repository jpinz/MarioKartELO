from player import Player


class ELOScoring:
    def __init__(self, max_rating_change, max_skill_gap):
        self.max_rating_change = max_rating_change
        self.max_skill_gap = max_skill_gap

    def updateScores(self, game, leaderboard=None):
        if leaderboard is None:
            leaderboard = []
        results = game.getResults()
        previous_scores = dict()

        for player in results:
            if player not in leaderboard:
                leaderboard.append(player)
            previous_scores[player.name] = player.elo

        for player_a in results:
            for player_b in results:
                if player_a.name == player_b.name:
                    continue
                p_a = leaderboard[(leaderboard.index(player_a))]

                chance_of_player_a_winning = self.chance_of_winning(previous_scores[player_a.name],
                                                                    previous_scores[player_b.name])

                if self.players_draw(player_a, player_b):
                    continue

                did_player_a_win = self.player_a_won(player_a, player_b)
                adjusted_rating_change = self.rating_change(chance_of_player_a_winning, did_player_a_win, len(results))
                integer_rating_change = round(adjusted_rating_change)
                if integer_rating_change == 0:
                    if adjusted_rating_change > 0:
                        integer_rating_change = 1
                    elif adjusted_rating_change < 0:
                        integer_rating_change = -1

                p_a.add_points_to_elo(integer_rating_change)

        return leaderboard

    def set_position(self, leaderboard):
        leaderboard = sorted(leaderboard, key=Player.get_elo, reverse=True)
        j = 1
        for player in leaderboard:
            player.position = j
            j += 1

    def player_a_won(self, player_a, player_b):
        return player_a.points > player_b.points

    def players_draw(self, player_a, player_b):
        return player_a.points == player_b.points

    def chance_of_winning(self, rating_a, rating_b):
        return 1 / (1 + pow(10.0, ((rating_b - rating_a) / self.max_skill_gap)))

    def rating_change(self, expected_to_win, actually_won, total_players):
        w = 1 if actually_won else 0
        return self.max_rating_change * (w - expected_to_win) / (total_players - 1)
