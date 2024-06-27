# Challenge Documentation

## Part 1: Model implementation

### Changes in exploration notebook

- Given a column in the features, the *delay rate* for each value taken by the column is computed as the percentage of delayed flights in that category. [Associated commit](https://github.com/tryolabs/tintin-challenge-tryolabs-latam/commit/bed404d0071cc95a545f29b47477f36a596a314f).

- Minor bugs were fixed,  such as [naming the arguments in `sns.barplot`](https://github.com/tryolabs/tintin-challenge-tryolabs-latam/commit/24487ef5eee651cb23e2c067b8f09f8941558c06), and [boundary cases in the get_period variable not being contemplated](https://github.com/tryolabs/tintin-challenge-tryolabs-latam/commit/4629556eda3db12684e11e30f99fbf129311d9a3).

**REMARKS**

- It has been noticed that the selected top features, are not exactly the ones with greatest importance, since `GRUPO_Copa Air` and `MES_11` are not in the top 10, while `MES_6` and `MES_8` are. However, I have decided not to change those features, since the tests seem to work with the 10 features that were originally used in the exploration notebook, and the README saying 

- I had to change the version of a few libraries in the `requirements.txt` to solve a few conflicts between dependencies.

>**It is not necessary to make improvements to the model**

- It was noticed that the splitting of the data in the notebook was done randomly. That can lead to data leakage, since there can be relations between delayed flights that are close in time (a delay in one flight, can cause delays in following flights). I fixed that in a [now discarded notebook](https://github.com/tryolabs/tintin-challenge-tryolabs-latam/blob/0c1898e5c3b8a9f00d518947908d4b0754eee466/challenge/exploration_all_features.ipynb). The notebook was later discarded because I saw that the tests were still doing a random splitting instead of splitting by time (like using the first 70% of the flights for training and the remaining for testing).
- Some features were never considered when studying feature importance. Some of them are features that were present from the beginning (such as the day of the month, the day of the week, the time, and those regarding the origin and destination of the flight), and some that were generated earlier from these (such as the `high_season` and the `period_day` features). A more thorough study of these features was done (in the [now discarded notebook](https://github.com/tryolabs/tintin-challenge-tryolabs-latam/blob/0c1898e5c3b8a9f00d518947908d4b0754eee466/challenge/exploration_all_features.ipynb) mentioned earlier), where I considered doing one-hot encoding of origin, destination and for the day of the week, and also mapped periodic time variables into a circle (for example the time, the day of the week, the month and the day of the month) using trigonometric functions. 
- I noticed that (before filtering by feature importance), TIPOVUELO was one-hot encoded, eventhough it only takes 2 values ('I' or 'N'). I feel like it makes more sense to only treat it as a single binary column (indicating if it is international or not), instead of the one-hot encoding. I did that change in the [discarded notebook](https://github.com/tryolabs/tintin-challenge-tryolabs-latam/blob/0c1898e5c3b8a9f00d518947908d4b0754eee466/challenge/exploration_all_features.ipynb) mentioned earlier. It is not that important at the end, since after filtering by feature importance you only used the category TIPOVUELO_I.

### Model implementation

- A minor bug regarding changing the type of brackets for `Union` (which should use square brackets instead of curly brackets) was done.
- I selected the XGBoost model with the 'top 10' features and balancing (the scale factor for the balancing is computed inside the fit method instead of just hardcoded, and therefore the model was re initialized to have that particular scale factor).
- I also needed to save the trained models, because during tests I had an error saying that it couldn't do predictions since the model was never trained. I also needed to load the latest trained model in the prediction method whenever the model hasn't been yet trained.
- My preprocessing method replaced all the get_dummies that was done to do all the one-hot encodings of the features, because during inference we might need to preprocess inputs that don't have all the values we need (for example, if Copa Air was not present in the input, then I wouldn't be able to get the OPERA_Copa Air feature from a get_dummies).

### Test
- The path to the data in the test had to be changed, since we are running the tests from the main folder of the repository.
- As it was explained before, while testing the prediction method in `test_model_predict`, since that test doesn't run the training method and (for some reason) the model was not keeping the trained version of the model that it got after running the `test_model_fit` test. Therefore, I decided to save the models locally when training in my training method, and to load the most recent version of the model whenever we try to do a prediction with an untrained model in my prediction method.

## Part 2: Deploy model to API
- To do a prediction using the API, I first needed to aggregate the inputs to a single pandas dataframe, preprocess the dataframe, and then run the model to output the predictions.
- A few validation methods were added in the schema classes for the input, in order to verify that the month is between 1 and 12, that the airline is valid (the list of airlines was obtained from all the airlines in our dataset), and to verify that TIPOVUELO is either I (international) or N (national).


## Part 3: Deploy API to GCP

To deploy our API to GCP, I had to:

1. Fill the Dockerfile
1. Install Google SDK
1. Authentify my Google account
1. Configure docker to use gcloud (with `gcloud auth configure-docker`)
1. Create a project in GCP, which was called `acastro-tryolabs-latam`
1. Build the docker `docker build -t gcr.io/acastro-tryolabs-latam/flight-predictor . --platform linux/amd64`. The flag `--platform linux/amd64` is there because an error I had when deploying it later, which seems to be a common problem with M1 chips like the one I'm using. The actual error was ` Application failed to start: failed to load /bin/sh: exec format error`, and that flag seems to fix the issue. In the command line to build the docker, you can see that my application was named `flight-predictor`.
1. Push the docker image to gcr, with `docker push gcr.io/acastro-tryolabs-latam/flight-predictor` 
1. Deploy with gcloud: `gcloud run deploy flight-predictor-api --image gcr.io/acastro-tryolabs-latam/flight-predictor --platform managed --region us-central1` 
1. Replace the API's URL (which is `https://flight-predictor-api-emdlm4e4fa-uc.a.run.app/predict`) in the makefile.

Here I needed to change the version of locust in the `requirements-test.txt`, since I needed to use a more recent version of Flask to avoid a couple problems with imports (`cannot import name 'escape' from 'jinja2'` and `cannot import name 'json' from 'itsdangerous'`). This error only ocurred when running the test for this part, but it was solved using a more recent version of locust.

Apart from the tests, I also tested the application by running the command line

```bash
curl -X POST "https://flight-predictor-api-emdlm4e4fa-uc.a.run.app/predict" \  -H "Content-Type: application/json" \  -d '{"flights": [{"OPERA": "Grupo LATAM", "TIPOVUELO": "N", "MES": 3}]}'
```

and it returned the prediction
```bash
{"predict":[0]}
```

## Part 4: CI & CD

