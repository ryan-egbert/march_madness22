class Game:
    def __init__(self, team1, team2, score, meta):
        self.team1 = team1
        self.team2 = team2
        self.score = score
        self.year = meta['year']
        self.round = meta['round']
        self.region = meta['region']

    def to_dict(self):
        return {
            'team1': self.team1,
            'team2': self.team2,
            'team1score': self.score['team1'],
            'team2score': self.score['team2'],
            'year': self.year,
            'round': self.round,
            'region': self.region
        }