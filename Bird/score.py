import json
# 处理排行
def savescore(username, score):
    file = open("score.json", 'r')

    try:
        data = json.load(file)
    except json.decoder.JSONDecodeError:
        data = {}
    if username in data.keys():
        if data[username] <= score:
            data[username] = score
    else:
        data[username] = score
    file.close()
    file = open("score.json", 'w')
    json.dump(data, file)
    file.close()


def getscore():
    file = open("score.json", 'r')
    data = json.load(file)
    '''

    print(type(data))
    print(data)
    '''
    sorted_data = sorted(data.items(), key=lambda x: x[1], reverse=True)
    file.close()
    if len(sorted_data) >= 3:
        return sorted_data[:3]
    else:
        return sorted_data[0:]
