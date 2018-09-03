def make_batches(size, batch_size): #size:全バッチの数  batch_size:いくつごとに処理するか
    '''
    #size:サンプルの数  batch_size:バッチの大きさ。サンプルをいくつの塊にするか
    num_batch:バッチの数
    return: list of tuples of array
            for i in range(num_batches):i=0からi=num_batchesまでi+=1になる
            i*batch_sizeで、size中のバッチの先頭
            min(size, (i + 1) * batch_size))で、size中のバッチの後尾 sizeが最大値（）
    '''
    num_batches = (size + batch_size - 1) // batch_size #バッチの数
    return [(i * batch_size, min(size, (i + 1) * batch_size))
            for i in range(num_batches)]