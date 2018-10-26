from player import Player
import itertools
import math


class ELOScoring:
    def __init__(self, max_rating_change, max_skill_gap):
        self.max_rating_change = max_rating_change
        self.max_skill_gap = max_skill_gap

    def predictScores(self, game, leaderboard=None):
        # If this is the first run, there will be no leaderboard
        if leaderboard is None:
            return "There isn't yet a leaderboard!"
        results = game.getResults()

        scores = dict()
        output = ""

        # Get each player in the game
        for player in results:
            if player not in leaderboard:  # see if the player is new
                return "Can't predict! {} isn't a valid person in the leaderboard.".format(player.name)
            # Get the player's previous (current) elo before calculations are made
            scores[player.name] = leaderboard[(leaderboard.index(player))].elo

        for player_a, player_b in itertools.combinations(results, 2):
            # Calculate the chance that Player A should win this game based on their elo
            chance_of_player_a_winning = self.chance_of_winning(scores[player_a.name],
                                                                scores[player_b.name])
            print("Player A ELO: " + str(scores[player_a.name]))
            print("Player B ELO: " + str(scores[player_b.name]))
            print(chance_of_player_a_winning)

            output += "There is a {0:.2%} chance that {1} will beat {2}.\n".format(
                chance_of_player_a_winning, player_a.name, player_b.name)

        return output

    def updateScores(self, game, leaderboard=None):
        # If this is the first run, there will be no leaderboard
        if leaderboard is None:
            leaderboard = []
        results = game.getResults()  # Just get the names of each player, and their final score
        # but results is an array of player objects, their elo is 1000, place and games played is 0

        # Create dictionaries for the previous elos, and the net change of elo per player
        previous_scores = dict()
        elo_change = dict()

        # Get each player in the game
        for player in results:
            if player not in leaderboard:  # see if the player is new
                leaderboard.append(player)
            # Get the player's previous (current) elo before calculations are made
            previous_scores[player.name] = leaderboard[(leaderboard.index(player))]
            # Add the player to the dict for changed elo to add to them at the end of the calculations
            elo_change[player.name] = 0

        # Loop through each player and calculate their elo against the other players (with permutation)
        for player_a, player_b in itertools.permutations(results, 2):
            print("Player A: " + player_a.name + " vs. Player B: " + player_b.name)

            a_elo = previous_scores[player_a.name].elo
            b_elo = previous_scores[player_b.name].elo

            did_player_a_win = self.player_a_won(player_a, player_b)

            if did_player_a_win:
                victory_multiplier = math.log(abs(int(player_a.points) - int(player_b.points)) + 1) * \
                                     (2.2 / ((a_elo - b_elo) * 0.001 + 2.2))
            else:
                victory_multiplier = math.log(abs(int(player_b.points) - int(player_a.points)) + 1) * \
                                     (2.2 / ((b_elo - a_elo) * 0.001 + 2.2))

            print("Victory multiplier: " + str(victory_multiplier))
            # Calculate the chance that Player A should win this game based on their elo
            print(player_a.name + " - " + str(a_elo))
            print(player_b.name + " - " + str(b_elo))
            chance_of_player_a_winning = self.chance_of_winning(a_elo, b_elo)

            tied = False

            # Don't change the elo if they tied
            if self.players_draw(player_a, player_b):
                victory_multiplier = 1
                tied = True

            # Did player A have a higher score than Player B
            # print(player_a.name + " - " + str(player_a.points))
            # print(player_b.name + " - " + str(player_b.points))

            # Calculate how much player A's elo should change based on their chances and if they won against B
            adjusted_rating_change = self.rating_change(chance_of_player_a_winning, did_player_a_win, len(results),
                                                        victory_multiplier, tied)

            print(player_a.name + " chance won: " + str(chance_of_player_a_winning) + " did win: " +
                  str(did_player_a_win) + " adjusted rating change:" + str(adjusted_rating_change))

            integer_rating_change = round(adjusted_rating_change)  # round the score to change the elo

            elo_change[player_a.name] += integer_rating_change  # add the elo change to their net change in the dict

            print(player_a.name + " rating change " + str(integer_rating_change))

            print(player_a.name + " net rating change " + str(elo_change[player_a.name]))
            # print("player_a new elo: " + str(player_a.elo + elo_change[player_a.name]) + " player_a: " + str(
            #    previous_scores[player_a.name].elo) + "\n")

        # Now that calculations are done, change each player's elo
        for player in previous_scores.values():
            player.add_points_to_elo(elo_change[player.name])

        return leaderboard

    # Update each player's position based on elo
    def set_position(self, leaderboard):
        leaderboard = sorted(leaderboard, key=Player.get_elo, reverse=True)
        j = 1
        for player in leaderboard:
            player.position = j
            j += 1

    # Did player A win?
    def player_a_won(self, player_a, player_b):
        return player_a.points > player_b.points

    # Did Player A and B draw/tie?
    def players_draw(self, player_a, player_b):
        return player_a.points == player_b.points

    # ELO standard calculation to calculate Player A's chance of beating Player B
    def chance_of_winning(self, rating_a, rating_b):
        return 1 / (1 + pow(10.0, ((rating_b - rating_a) / self.max_skill_gap)))

    # ELO standard calculation to calculate the change of Player A's elo based on outcome
    def rating_change(self, expected_to_win, actually_won, total_players, victory_multiplier, tied):
        if actually_won and not tied:
            w = 1
        elif tied:
            w = 0.5
        else:
            w = 0
        return (self.max_rating_change * victory_multiplier) * (w - expected_to_win) / (total_players - 1)
