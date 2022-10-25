class Fruit():
    def __init__(self, x, y, size = 10, energy = 100, reductionValue = 1.5):
        self.x = x; self.y = y
        self.size = size
        self.energy = energy      # Energy obtained for 0 aggressiveness, maybe determine from size
        self.reductionValue = reductionValue # How much aggressiveness causes energy value to decrease, ideally 1 to 2
    
    def getReducedEnergy(self, aggressiveness):
        return self.energyValue * (1 - aggressiveness)**self.reductionValue
