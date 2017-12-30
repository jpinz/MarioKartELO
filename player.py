class Player:
    def __init__(self, name, elo, position, points, games_played):
        self.name = name
        self.elo = elo
        self.points = points
        self.position = position
        self.games_played = games_played

    def set_elo(self, new_elo):
        self.elo = new_elo

    def get_elo(self):
        return self.elo

    def set_points(self, points):
        self.points = points

    def get_points(self):
        return self.points

    def add_points_to_elo(self, points):
        self.elo += points

    def add_game(self):
        self.games_played += 1

    def __eq__(self, other):
        return self.name == other.name

    def __cmp__(self, other):
        if self.name == other.name:
            return 0
