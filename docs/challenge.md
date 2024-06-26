# Challenge Documentation

## Part 1: Model implementation

### Changes in exploration notebook

- Given a column in the features, the *delay rate* for each value taken by the column is computed as the percentage of delayed flights in that category. [Associated commit](https://github.com/tryolabs/tintin-challenge-tryolabs-latam/commit/bed404d0071cc95a545f29b47477f36a596a314f).

- Minor bugs were fixed,  such as [naming the arguments in `sns.barplot`](https://github.com/tryolabs/tintin-challenge-tryolabs-latam/commit/24487ef5eee651cb23e2c067b8f09f8941558c06), and [boundary cases in the get_period variable not being contemplated](https://github.com/tryolabs/tintin-challenge-tryolabs-latam/commit/4629556eda3db12684e11e30f99fbf129311d9a3).

**REMARKS**

- It has been noticed that the selected top features, are not exactly the ones with greatest importance, since `GRUPO_Copa Air` and `MES_11` are not in the top 10, while `MES_6` and `MES_8` are. However, I have decided not to change those features, since the tests seem to work with the 10 features that were originally used in the exploration notebook, and the README saying 

>**It is not necessary to make improvements to the model**

- It was noticed that the splitting of the data in the notebook was done randomly. That can lead to data leakage, since there can be relations between delayed flights that are close in time (a delay in one flight, can cause delays in following flights). I fixed that in a [now discarded notebook](https://github.com/tryolabs/tintin-challenge-tryolabs-latam/blob/0c1898e5c3b8a9f00d518947908d4b0754eee466/challenge/exploration_all_features.ipynb). The notebook was later discarded because I saw that the tests were still doing a random splitting instead of splitting by time (like using the first 70% of the flights for training and the remaining for testing).
- Some features were never considered when studying feature importance. Some of them are features that were present from the beginning (such as the day of the month, the day of the week, the time, and those regarding the origin and destination of the flight), and some that were generated earlier from these (such as the `high_season` and the `period_day` features). A more thorough study of these features was done (in the [now discarded notebook](https://github.com/tryolabs/tintin-challenge-tryolabs-latam/blob/0c1898e5c3b8a9f00d518947908d4b0754eee466/challenge/exploration_all_features.ipynb) mentioned earlier), where I considered doing one-hot encoding of origin, destination and for the day of the week, and also mapped periodic time variables into a circle (for example the time, the day of the week, the month and the day of the month) using trigonometric functions. 
- I noticed that (before filtering by feature importance), TIPOVUELO was one-hot encoded, eventhough it only takes 2 values ('I' or 'N'). I feel like it makes more sense to only treat it as a single binary column (indicating if it is international or not), instead of the one-hot encoding. I did that change in the [discarded notebook](https://github.com/tryolabs/tintin-challenge-tryolabs-latam/blob/0c1898e5c3b8a9f00d518947908d4b0754eee466/challenge/exploration_all_features.ipynb) mentioned earlier. It is not that important at the end, since after filtering by feature importance you only used the category TIPOVUELO_I.

### Model implementation

- A minor bug regarding changing the type of brackets for `Union` (which should use square brackets instead of curly brackets) was done.
- I selected the XGBoost model with the 'top 10' features and balancing.
- I also needed to save the trained models, because during tests I had an error saying that it couldn't do predictions since the model was never trained. I also needed to load the latest trained model in the prediction method whenever the model hasn't been yet trained.





## Part 2: Deploy model to API

## Part 3: Deploy API to GCP

## Part 4: CI & CD