ALL_INDEXES = {
    0: 'Index0',
    1: 'Index1',
    2: 'Index2',
    3: 'Index3',
    4: 'Index4',
    5: 'Index5',
    6: 'Index6',
    7: 'Index7',
    8: 'Index8',
    9: 'Index9'
}


def selectInRange(selected, newSelection):
    newIndex = newSelection["index"]
    minIndex = -1
    maxIndex = -1

    for task in selected:
        if minIndex == -1 or task["index"] < minIndex:
            minIndex = task["index"]
        if maxIndex == -1 or task["index"] > maxIndex:
            maxIndex = task["index"]
    
    print(minIndex, maxIndex)

    # if minIndex > newIndex:
    #     newRange = list(range(newIndex, minIndex))
    # elif newIndex > maxIndex:
    #     newRange = list(range(maxIndex, newIndex))
    newRange = list(range(min(newIndex, maxIndex), max(minIndex, newIndex)+1))
    for i in newRange:
        selected.append({
            'value': ALL_INDEXES[i],
            'index': i
        })
    
    result = sorted(selected, key=lambda x: x['index'])
    return result
    


def main():
    selected = [
        # {'value': 'Index2', 'index': 2},
        # {'value': 'Index3', 'index': 3},
        {'value': 'Index4', 'index': 4}, 
        {'value': 'Index5', 'index': 5}
    ]
    newIndex = {'value': 'Index7', 'index': 7}
    result = selectInRange(selected, newIndex)
    print(result)
    newIndex = {'value': 'Index8', 'index': 8}
    result = selectInRange(selected, newIndex)
    print(result)


if __name__ == "__main__":
    main()