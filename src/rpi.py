




def parse_int(int_str):
    try:
        res = int(int_str)
        return res
    except ValueError as e:
        print(f"Invalid param passed {int_str}")
        return None

def get_win_percentage(record_string):
    if not isinstance(record_string, str):
        print("Value is not a string.")
        return -1
    record = record_string.split("-")
    if len(record) > 2:
        print(f"Invalid record string passed. {record_string}")
        return -1
    wins = parse_int(record[0])
    losses = parse_int(record[1])

    if wins and losses:
        return wins/(wins+losses)
    else:
        return -1

def get_avg_opp_wp(games):
    pass



print(get_win_percentage("10-1"))
print(get_win_percentage("$-1"))
print(get_win_percentage(10))