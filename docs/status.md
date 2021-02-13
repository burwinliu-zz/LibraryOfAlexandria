
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
 
Our current approach is using a greedy algorithm to minimize the steps to get the result. Our current algorithm 
supports a single retrieval step and gathers the correct amount of requested goods from the simulated user requests. 
By using this algorithm we have set a baseline heuristic in order to complete our retrieval goal. Our agent only has
knowledge of the chest contents and it's own inventory contents. Based on these two observations and the simulated 
users goal value the agent searches through the chests to find the correct amount of materials in the chest. As the
agent moves through the chests it takes the required amount of materials that the goal user asked for until it has 
reached the goal value. This approach currently doesn't support swapping items in chests to make future runs faster 
which is one of the things planned for the future. The current setup and heuristic only being the user simulated goal 
is also something we need to work on and we will be adding more heuristics in order to improve the search capability. 
The current actions are agent can do is open and close chests take items in and out of the chests and place them into 
the goal chest at the end of its mission. 

## Evaluation

Qualitative

Quantitative

To support our method as well as show clear signs where we can improve the method we ran our test which consisted of a simulated user giving one command to gather a certain amount of materials 100 times and compared this to a normalized based on the amount of items requested and the distribution of the materials. 


This data shows that our algorithim doesn't really improve but gives us a good baseline to work off of 

## Future Plans
Currently, we have essentially created a very simple case that would (theoretically) be the fastest traversal over all 
chests. However,
## Resources
