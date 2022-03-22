ids = {}
with open('id_name.csv', 'r') as f:
    linenum = 1
    for line in f:
        l = line.replace('\n','').split(',')
        team1name = l[6]
        team2name = l[7]
        team1id = l[10]
        team2id = l[11]
        if team1name in ids:
            print(linenum, team1name, ids[team1name], '==', team1id)
            assert ids[team1name] == team1id
        else:
            ids[team1name] = team1id
        
        if team2name in ids:
            print(linenum, team2name, ids[team2name], '==', team2id)
            assert ids[team2name] == team2id
        else:
            ids[team2name] = team2id

        linenum += 1