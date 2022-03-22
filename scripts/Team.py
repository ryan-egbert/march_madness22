class Team:
    def __init__(self, id, meta):
        self.id = id
        self.name = meta['name']
        self.year = meta['year']
        self.stats = meta['stats']

    def to_dict(self):
        return {
            'ID': self.id + self.year,
            'id_num': self.id,
            'name': self.name,
            'year': self.year,
            'stats': self.stats_to_dict()
        }

    def stats_to_dict(self):
        return {
            'PTS': self.stats[3],
            'REB': self.stats[4],
            'AST': self.stats[5],
            'STL': self.stats[6],
            'BLK': self.stats[7],
            'TO': self.stats[8],
            'FG%': self.stats[9],
            'FT%': self.stats[10],
            '3P%': self.stats[11],
        }

    def add_record(self, meta):
        self.record = meta['record']
        self.home = meta['home']
        self.away = meta['away']
        # self.margin = meta['margin']
        # self.bpi = meta['bpi']
        # self.q1 = meta['q1']
        # self.sor = meta['sor']
        # self.sos = meta['sos']

class TeamGroup:
    def __init__(self):
        self.teams = []

    def add_team(self, team):
        self.teams.append(team)

    def add_team_record(self, team, year, meta):
        for team in self.teams:
            if team.name == team and team.year == year:
                team.add_record(meta)
    
    def find_team(self, by, value):
        if by == 'id':
            team = self._find_team_by_id(value)
        elif by == 'name':
            team = self._find_team_by_name(value)
        else:
            team = None
        return team

    def _find_team_by_id(self, id):
        for team in self.teams:
            if team.id == id:
                return team
        return None

    def _find_team_by_name(self, name):
        for team in self.teams:
            if team.name == name:
                return team
        return None
