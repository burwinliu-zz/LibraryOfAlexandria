---
layout: default
title: proposal
---

# Proposal
## Overview
This is a Proposal page for our project: Library of Alexandria

## Summary
Our goal is to make an intelligent agent sort, move and retrieve various items in a preconstructed area. In terms of input, we will provide an enviornment to train the agent in, where it may place objects, and some command that will indicate the user's desires. The applications for this project is as follows: 
- First, we are creating an agent of convinience for players in the future -- if they so choose, providing them an easy way to sort through massive inventories in an intuitive manner
- Second, we are creating an agent that can model an intelligent agent, which may be used in real world applications, for retrieving items from an inventory in a warehouse for instance

## AI/ML Algorithm
As we are right now in the initial stages of development, we imagine we will be using NLP for retrieval and some form of a graph search to find locations for certain items

## Evaluation
Our main metric would be the time for the agent to store/retrieve items. Assuming the baseline method for users to retrieve items is to manually look through every chest, the user would have to take a good amount of time on average to find the item. We hope to reduce this time to a just few seconds per job, allowing for quick retrival of items within the preset storage space. We will have our bot run many retrieval missions and record the average times to be used for our quantitative evaluation. 

Our qualitative analysis will depend on first completing basic tasks as a sanity check, such as recieving items from chests in linear and strightforward scenarios (ie. one chest few items, with relatively simple commands). We will check to see if the object retrieved corresponded to what we issued our command for. As our scope evolves we will also add the element of complexity in storage and recall tasks by the agent. To visualize our algorithim we will use graphs to plot performance, and overlay competing algorithims to ensure we are using the most efficient algorithim. We will also expirement with the level of complexity our agent can handle and make changes based off performace in each case. Our moonshot case that could be interesting is recalling items and using them to speed up the search ie. first chest has an ender pearl so the agent throws it to get to its next search location faster. 

## Appointment
Appointment Date/Time: Friday Jan 22, 2:15pm

<br><br><br><br><br>