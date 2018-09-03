
def make_features(position):
    width, height, own_a1, own_a2, opponent_a1, opponent_a2, value, state = position
    features = make_input_features(width, height,value, state)

def make_input_features():