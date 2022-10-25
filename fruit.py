class Fruit():
    def __init__(self, x, y, size = 10, energyValue = 50, reductionValue = 1.5):
        self.x = x; self.y = y
        self.size = size
        self.energyValue = energyValue      # Energy obtained for 0 aggressiveness
        self.reductionValue = reductionValue # How much aggressiveness causes energy value to decrease, ideally 1 to 2
    
    def getReducedValue(self, aggressiveness):
        return self.energyValue * (1 - aggressiveness)**self.reductionValue
