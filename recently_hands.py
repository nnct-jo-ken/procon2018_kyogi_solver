# coding: utf-8

DEBUG = False

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

    def check(self, hand, times = 3):
        if self.hands.count(hand) >= times: #同じ手が{times}回以上行われている
            if DEBUG is True:
                print("recently hands", self.hands, "count", self.hands.count(hand))
            return False    #同じ手が規定数以上

        return True #同じ手が規定数以内
