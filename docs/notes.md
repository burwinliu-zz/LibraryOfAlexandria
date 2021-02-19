Time to store items, (Low weight? Who cares how long to store -- vs high weight?)


More weight to retrieving items (cost to retrieving)
Space used ? maybe ... (moon shot)


optimized under some constraints -- probability and distribution about what user wants that is given, placing system optimized given distribution.

constraints satisfactions, costs assosciated to search, A* search, or Greedy Search.

Enviornment First. Objective function, mathmatically. Keep a single enviornment, line of chests (easier to denote everything that way, descide based on that)
    Reinforcement Learning vs Optimization -- Think about states -- what kind of algorithm to study? 

Section on goals -- environment + brute force, simple setup, how to run 

And weekly meeting time to schedule 



## Proposal
Enviornment, Line of chests

Problem -- fastest way to retrieve objects 

Environment 

Probability Distribution -- uniform distribution 


input: [ presumed values for chests (w/-1 for unknowns?) ], position (maybe global/class object), desired items (passed as params)

use presumed values and position to calculate costs for each position, create estimate based on "removed items" and known distribution, and calculate cost/reward to explore, train the agent based on these principles,

1) Can we vary the env? Removing the items as we go along and then 


Distribute according to some distribution per chest

	Keep env constant, and 
	RLib -> Obs space, to model, action space, -> (iterative learning) Inventory + looking for + what you are at