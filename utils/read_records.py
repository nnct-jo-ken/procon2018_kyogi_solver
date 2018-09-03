def read_records(record_list_file):
    records = []
    with open(record_list_file, 'r') as f:  #対局データファイルを開く
        for line in f.readlines():  #行ごとに
            filepath = line.rstrip('\r\n')  #ファイルパスを抜き出す
            records.append(filepath)    #リストに追加
    return records