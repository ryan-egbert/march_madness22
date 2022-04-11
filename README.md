# March Madness Prediction Model 2022
## Data
This is a model that I used to predict the outcome of the games during the 2022 NCAA Men's Basketball Tournament. Data was obtained from [data.world](https://data.world/michaelaroy/ncaa-tournament-results), [Kaggle](https://www.kaggle.com/competitions/mens-march-mania-2022), and scraped from [ESPN](https://www.espn.com/). 

Scripts used for scraping data are located in ```./scripts/```.

Data was stored in a local MongoDB database, holding individual team and game data.

The data used in the model training can be found in ```./MARCH_MADNESS_DATA.csv```

## Model
The final model can be found in ```./FINAL_MODEL.ipynb```. Submissions and predicions can be found in ```./sumissions/``` and ```./predictions/```, respectively.

## About the Project
In 2020, I created a March Madness "Simulator" to determine who would have won the tournament that was cancelled due to COVID-19. In 2022, I wanted to improve the model and see if I could correctly identify the winners of each of the March Madness games.

On this [Kaggle competition](https://www.kaggle.com/competitions/mens-march-mania-2022/leaderboard), the model performed very well, placing 23rd out of nearly 1000 participants.

## Contact
For more information, feel free to reach out to me at (ryanegbert15@gmail.com)[mailto:ryanegbert15@gmail.com].