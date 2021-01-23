---
layout: default
title: Proposal
---

# Proposal
## Overview
This is a Proposal page for our project: Library of Alexandria

## Summary

Our goal is to make an intelligent agent that will quickly retrieved stored objects in a constructed area. 

In more detail, our project's goal will be to optimize the retrieval time of objects from a storage space. Our enviornment will be a straight row of chests, with our agent, a machine controlled character. Our program will take a main input being a stream of inputs and output requests, which would simulate a user passing objects onto the machine to stow and then a list of objects to retrieve. The inputs will be randomized over some probability distribution, to simulate a user requesting for objects. The Actor will store our inputted items stored, then, on recieiving inputs to retrieve, will begin retrieving those objects specified. Our output for this project will be the average time to retrieve an object given our algorithm. The resulting goal should be to minimize this output through a series of techniques, and taking advantage of our sorting!

The applications for this project is as follows: 
- First, we are creating an agent of convinience for players in the future -- if they so choose, providing them an easy way to sort through massive inventories in an intuitive manner
- Second, we are creating an agent that can model an intelligent agent, which may be used in real world applications, for retrieving items from an inventory in a warehouse for instance

## AI/ML Algorithm
With some revision, we believe that our Algorithm will be a sorting and optimization algorithm, that given the probability distribution, we can construct a sorting algorithm to understand the best placement of our items. Furthermore, we will use some form of a greedy algorithm (likely, find the location of the furthest object, run to that position, retrieve items, and continue retrieving all items along the way back) to retrieve our items.

## Evaluation
Our main metric would be the time for the agent to store/retrieve items. Assuming the baseline method for users to retrieve items is to manually look through every chest, the user would have to take a good amount of time on average to find the item. We hope to reduce this time to a just few seconds per job, allowing for quick retrival of items within the preset storage space. We will have our bot run many retrieval missions and record the average times to be used for our quantitative evaluation. 

Our qualitative analysis will depend on first completing basic tasks as a sanity check, such as recieving items from chests in linear and strightforward scenarios (ie.one row of chests and very few items to sort). We will check to see if the object retrieved corresponded to what we issued our command for. As our scope evolves we will also add the element of complexity in storage and recall tasks by the agent by providing more varied inputs for our Agent. A moonshot case would be to provide a mixed input, with inputs and outputs streaming in, and have the agent resort the chests on the fly to optimize over all time to retrieve objects when asked to do so. 

## Appointment
Appointment Date/Time: Friday Jan 22, 2:15pm

## Group Meeting Time
Fridays, 2:00 pm

<br><br><br><br><br>