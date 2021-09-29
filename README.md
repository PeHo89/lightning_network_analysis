# Lightning Network Analysis
A repository of the source code used in my master thesis **Payment Channel Network Analysis with Focus on Lightning Network** at the Vienna University of Technology (masters course *Software Engineering and Internet Computing*)

## Description
This repository contain three parts which were developed in the scope of my master thesis:

* Analysis Part - Jupyter Notebook:
    * Analyses about the Lightning Network such as Size, Balances, Locations, etc.
    * Analyses about the Bitcoin blockchain such as 2-of2 multi-signature transactions, potential Lightning Network channel transactions, etc.

* Entity-Node-Mapping Part - 4 Step Python Scripts:
    * Enrich Lightning Network channels with data from GraphSense [1,2]
    * Map GraphSense entities to channels and nodes
    * Improve entity node mapping by cross-checking mechanisms

* Archive Part - Python Script:
    * Several Analyses and figures (exploratory)

## Prerequisites
* `./data/data.zip.001`-`./data/data.zip.033` files extracted together in one step to `./data/` directory (split archive)

* Access to GraphSence [1,2]

* `.env_template` file renamed to `.env` and filled with valid GraphSense credentials (`GRAPHSENSE_USER` and `GRAPHSENSE_PASSWORD` variables)

## Content of Directory `./analyses/`
* `analyses.ipynb` create figures and numbers that were used in the results chapter of my master thesis (Jupyter notebook);

## Content of Directory `./enrich_and_map/`
* `1_enrich_channels.py` enrich Lightning Network channels with data from GraphSense, such as funding transaction input addresses, settlement transaction output addresses (if channel is already closed), GraphSense entities based on input and output addresses;
* `2_map_entities_channels.py` map enriched channels to entities separated on input and output entities;
* `3_map_entities_nodes.py` map nodes to entities based on mapped channels (heuristically);
* `4_improve_entity_node_mapping.py` increase the uniquely mapped entitites to nodes (heuristically) based on assumptions;

## Content of Directory `./archive/`
* `several_analyses_and_figures.py` exploratory create figures and numbers that were used during the development process of my master thesis;

## Author
Peter Holzer, BSc.<br>
peter.holzer89@gmail.com<br>
Matriculation Nr.: e01425797<br>
Vienna University of Technology

## References
[1] https://graphsense.info/<br>
[2] https://github.com/graphsense