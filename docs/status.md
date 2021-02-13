
## Video


## Project Summary
The goal of our project is to train a Minecraft agent to navigate an environment consisting of a row of n chests and 
1 goal chest to retrieve and store items in an efficient manner given a distribution of items. The distribution will 
be determined by a "simulated user" who will send retrieval and storage commands to the agent. The result of the 
retrieval commands will accumulate in the goal chest.  To do this the agent must optimize the placement of these 
items based on the retrieval requirements of the items. The final goal of this project would be to create an agent 
which can effectively store and retrieve items with the least amount of delays moving items around to optimize 
retrieval for each request.


## Approach
Our environment was a straight line of chests which each contain a random amount of distributed items. Each "type" of 
chest is marked by the block in front of it on the floor (see below); 
as follows: 
- Iron = mission complete (no chest)
- Emerald = result chest (chest to deposit the request after completion)
- Diamond = deposited chest (chest to hold some unspecified amount of items)


<img src="static/setup.png" style="width:1000px;"/>

Our agent is setup with several pieces of information and a simple action set. In terms of information, the agent has 
the probability distribution of the items passed, and has the ability to take a few discrete actions -- move left/right,
open/close chests and pick up certain items. 

Our current approach is to take a greedy approach, where we try and find the least number of moved steps to find the 
correct number of steps. In essence this becomes a simple traversal over the chests from the starting point to capture 
the needed items.



 

## Evaluation

Qualitative

Quantitative

## Future Plans
Currently, we have essentially created a very simple case that would (theoretically) be the fastest traversal over all 
chests. However,
## Resources
