# coding: utf-8

import socket
import game
import solver

DEBUG = False

field = game.field()        #フィールド作成
field.clear()   #フィールド情報をクリア

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket1:
    socket1.connect(("127.0.0.1", 12345))   #接続をする

    while True: #GUIが接続を切断するまで、ずっと続ける
        value_nums = [] #タイルの点数などを管理
        state_nums = [] #陣形などを管理

        value = socket1.recv(512)
        socket1.send(b'end')
        state = socket1.recv(512)

        value_lines = value.split(b':')
        for value_line in value_lines:
            nums = value_line.split(b' ')
            value_nums.append(nums)
        value_nums.pop(-1)  #末尾の余分なデータを削除

        state_lines = state.split(b':')
        for state_line in state_lines:
            nums = state_line.split(b' ')
            state_nums.append(nums)
        state_nums.pop(-1)

        if DEBUG is True:
            print(value_nums)
            print(state_nums)

        field.create_from_gui(value_nums, state_nums)   #読み取ったデータからフィールドの生成
        if DEBUG is True:
            field.print_field()

        # 移動方向の出力
        buffer = solver.solve(field)
        print(buffer)
        socket1.send(buffer.encode('utf-8'))
