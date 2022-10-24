# Thesis-Simulation
by Jordan Perry

Simulators the relationship between predator and prey using applicable physics forces.
Creatures will be driven by one of two methods:
1. a Machine Learning network that will take in inputs of its aggressiveness, the nearest sources of food, and nearest sources of danger and outputs of x and y components of force it would like to exert for movement. The network will then be passed o
2. a series of if statements determining what the creature should do in a situation based on it's aggressiveness (how likely it is to be a predator vs a prey).

There will be base food sources available for all creatures, which will be the only source if they have the lowest aggressiveness of all. The more aggressive a creature, the less energy that will be gained from eating these base food sources.
