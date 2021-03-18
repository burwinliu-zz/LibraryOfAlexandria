---
layout: default
title: Final Report
---

## Video

## Project Summary

The Library of Alexandria attempts to sort and optimize the retrieval for objects in an unpredictable enviornment. The problem was motivated by a librarian, attempting to store items with unlimited time, and retreive in a limited amount of time (presumably to keep their clients happy). Therefore, we attempted to create a problem that, in Minecraft, would simulate a similar situation -- with chests to represent storage spaces and inventory items as items to store. Our agent will try to distribute the item, then be measured based on their distribution. 

The basic idea of the problem follows this:
<ol>
    <li>The agent recieves some items to distribute, and distributes them in the enviornment</li>
    <li>The agent then retrieves the items, and is scored based on
        <ol>
            <li> Number of steps to retreieve the request </li>
            <li> Number of items from the request retrieved </li>
        </ol>
    </li>
</ol>

### Problem Setup 
I will describe the problem setup in 3 parts:
1. The Enviornment (where this problem will occur)
2. The Requester (the representation of the user)
3. The Rewards (how the performance of the actors will be determined)
       
### Environment Setup
The enviornment, will represent the "Library".

<img src="static/setup.png"/>

As you can see, we created a linear row of chests to represent this enviornment. There agent can stand in the second row only, with 3 "spots" the agent may reside in. 
These are as follows
1. The Grey (Iron) Blocks denotes that a run has completed, and acts as the "end mission" signal to our algorithm
2. The Green (Emerald) Blocks denotes the "result" chest, where requested items, if retrieved, will be deposited after the items have been retrieved
3. The Blue (Diamond) Blocks denotes the "library" chest, where the librarian will deposit the items to distribute for storage.

The Enviornment is held constant as shown in the image above, with 10 "Library" chests, and a single "Result" chest to the right of the rightmost "Library" chests, and an iron block to the right of that result chests. Therefore the enviornment will always be shown as thus (D = Library Chest, E = Result Chest, I = End Chest):

> [D, D, D, D, D, D, D, D, D, D, E, I]

With the current definition, this problem is trivial. However, our problem also has a bit of an issue -- when distributing in certain chests, they may have a chance, when retrieved, will not properly open, therefore, sealing the contents and preventing them from being retrieved. This moves the problem from being trivially easy to a problem to a problem warranting Machine Learning, which we will later demonstrate after explaining the rest of the setup.

The Agent is then spawned in on the Emerald Block, with an inventory full of items to distribute, which it will need to distribute, then recieve a request from the "Requester" agent, which will represent the user making requests of items. 

### Requester Setup
Our requester is setup so that 


### Rewards Setup



## Approaches
For our approach to solving this problem we employed PPO reinforcement learning, using RLib. To prove the efficacy of our approach, and the  we compared this against our benchmark employing the idea of the law of large numbers and placing the items in a algorithimic manner based on a simulated 10k requests by our "pateron" distribution. In our evaluation section we will go in depth in how our benchmark faired against our PPO algorithim and the precise improvements PPO had over our trivial brute force algorithim. 



### PPO reinforcement learning approach

In order to implement PPO reinforcement for this problem we first definied what the observation space for our agent would be. We decided that the observation space would consist of two main details:

1. The item the agent is about the place
2. All the items placed in the chests currently an their positions

### Encoding and Enviornment Setup
At first we created a 2 dimesional observation space where the items were assigned a number ex. stone=1, diamond=2, glass=3 so that we could represent the item as a integer in the observation space. The 2d observation space followed the following dimesions

(number_of_chests + 1, number_of_chest_slots) 

The reason we have number_of_chests + 1 rather than number_of_chests in our observation space is to hold the item the agent is about to place next we treat this item as an entirely new chest whose first position is filled in with the one hot encoded item that is to be placed next all other spots in this chest are always empty. This allowed us to maintain using a linear model and also eliminated the need to generate preprocessing or a custom observation space dimensions with little cost on training.

As seen in the image below our observation space was initially mapped as an array of the values below.
<img src="static/2d_observation.png"/>

After some research on one-hot encoding and a meeting with the TA we realized instead of assigning items to decimal numbers as the 2d observation space required we treat the items as one-hot encoded integers ex. stone=[1,0,0], diamond=[0,1,0], glass=[0,0,1]. This would improve our learning rate since our labels were non ordinal. This expanded our observation space to a three dimensional space. Where the new dimesions were

(number_of_chests + 1, number_of_chest_slots, unique_item_onehot) 

As seen in the image below our observation space ended up mapping to a 3d space.
<img src="static/one_hot_observation.png"/>

Once we decided our observation space we decided our action space. For this we essentially let the agent select a chest to put the item it is holding. Once at the chest it places the item in the closest empty slot in its observation space. We avoided giving individual steps like move left and move right and place object since our goal with the agent was not to navigate the environment but to place the items in the best slots.


The idea of figuring out the best slots is where our reward function plays its role. The agent recieves no reward until it has placed all the items once it has placed all the items which means our PPO algorithim has to deal with both sparse, delayed, and episodic rewards. The agent then recieves a request on a distribution based on a probability a "pateron" may select any specific item. Once the request is recieved the agent uses a simple algorithim to recieve the items going to the closest chest first. If it is able to open the chest then it takes its reward. If the agent cannot open the chest due to the chest being "locked" on the precentages we defined then it, then it will move through its memory of remaining chests until no more remain. If it fails to retrieve a given item, then it will be penalized
1. We allot a -1 reward for every step the agent takes to retrive the item.
2. We allot a -10 reward it the agent is not able to retrieve the item if the chest cannot be opened.
3. A -5 reward explained below

What we realized when implementing this was that after some training time our agent was taking a very long time to place the items. After some investigation we realized our agent was always finding the closest chest to be ideal for every item so in order to disuade the agent to try to place an item into a chest that is already full we attributed a  -5 reward when the agent fails to place the item. 


### Benchmark Approach

#### Benchmark Greedy

#### Benchmark Uniform

 
## Evaluation

## References

https://machinelearningmastery.com/why-one-hot-encode-data-in-machine-learning/
