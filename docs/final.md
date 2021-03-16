---
layout: default
title: Final Report
---

# Video

# Project Summary
The goal of the Library of Alexandria is to train an agent that can optimally place a variety of items in a set of n chests in a manner that can ensure that paterons who visit the Library can recieve the items they request and that they are recieved in the least amount of steps possible. As seen below our environment consists of 10 chests and the agent has a set of predefnined items dropped on the emerald square. The agent then picks up all these items and one by one decides where each of the items should be placed in the chests. We added additonal contraints to the chests where they have a random rate of failure.

In our case we generated this idea of the "pateron" by designing a distribution at which each item is requested at. 
# Approaches
For our approach to solving this problem we employed PPO reinforcement learning and we compared this against our benchmark employing the idea of the law of large numbers and placing the items in a algorithimic manner based on a simulated 10k requests by our "pateron" distribution. In our evaluation section we will go in depth in how our benchmark faired against our PPO algorithim and the precise improvements PPO had over our trivial brute force algorithim. 

####PPO reinforcement learning

In order to implement PPO reinforcement for this problem we first definied what the observation space for our agent would be. We decided that the observation space would consist of two main details:

1. The item the agent is about the place
2. All the items placed in the chests currently an their positions

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

The idea of figuring out the best slots is where our reward function plays its role. As opposed to traditional RL method of providing a reward after every action the agent recieves no reward until it has placed all the items once it has placed all the items. The agent then recieves a request on a distribution based on a probability a "pateron" may select any specific item. Once the request is recieved the agent uses a simple algorithim to recieve the items going to the closest chest first. If it is able to open the chest then it takes its reward. If the agent cannot open the chest due to the chest being "locked" on the precentages we defined then it skips retriving the item. We have all rewards defined as less than 0 so our agent tries to minimize the negative reward.

1. We allot a -1 reward for every step the agent takes to retrive the item.
2. We allot a -10 reward it the agent is not able to retrieve the item if the chest cannot be opened.
3. A -100 reward explained below

What we realized when implementing this was that after some training time our agent was taking a very long time to place the items. After some investigation we realized our agent was always finding the closest chest to be ideal for every item so in order to disuade the agent to try to place an item into a chest that is already full we attributed a massive -100 reward when the agent fails to place the item. 



 
# Evaluation

# References

https://machinelearningmastery.com/why-one-hot-encode-data-in-machine-learning/
