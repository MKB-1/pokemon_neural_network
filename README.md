# Pokemon Battle AI

  <p align="center">
  Replicated the Pokemon combat system using Python. Using webscrapped Pokemon Attacks from <a target="_blank" href="https://pokemondb.net/">Pokemon Database</a> and Pokemon Stats I had from my <a target="_blank" href="https://github.com/MKB-1/pokemon_viz">Pokemon Stat Visualization Project</a>, ran a Monte-Carlo simulation with randomly generated Pokemon. Used simulation results to train a neural network. <a target="_blank" href="">Try to beat my AI!</a> 
  </p>
</div>




<!-- ABOUT THE PROJECT -->
## About The Project
After my Pokemon Stats visualization project, I wanted to do a more complex project with the data I had. I thought it would be fun to simulate the combat system used in Pokemon games. Using Python and an Object-Oriented approach, I replicated the entire system from scratch. It was more complex than I realized, but not to difficult to implement. Since playing by yourself is no fun, I wanted to make an AI to fight. At this point, I had no idea how to do so &mdash; I had not yet learned of heuristics or search trees. However I had some experience with machine learning. But how could I use machine learning if I had no data? And what would this data even look like?
I decided I needed sequential data because Pokemon Battles usually last more than 1 turn.
To determine whether an attack was effective or not, I can look at the end of the sequence and see who won. I set a simple rule: an attack is effective if it leads to a victory.
I easily created this data with my battle simulator. Then, I used the data to train a neural network. At each turn, the neural network predicts the next attack which is on a path to victory.

Later, when I took an AI course, I realized that my approach was similar to a Monte-Cristo simulation!


### Built With

* Flask
* Numpy
* Pandas
* Scikit-Learn
