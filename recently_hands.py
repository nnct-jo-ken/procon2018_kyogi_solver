# coding: utf-8

class Recently_hands:
    def __init__(self, hands = None):
        if type(hands) is type([]):
            self.hands = hands
        elif hands is None:
            self.hands = []
        else:
            raise Exception('Queue Type Error!')

    def put(self, hand):
        if len(self.hands) == 9:
            del self.hands[0]    #9回前？の手を削除

        self.hands.append(hand)
        return self.hands

    def get(self):
        try:
            hand = self.hands.pop()

            return hand, self.hands
        except IndexError:
            return None

    def check(self, times = 3):
        for hand in self.hands:
            if self.hands.count(hand) >= times: #同じ手が{times}回以上行われている
                return False    #同じ手が規定数以上

        return True #同じ手が規定数以内
