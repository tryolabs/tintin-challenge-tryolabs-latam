# Challenge Documentation

## Part 1: Model implementation

I decided to use the feature selection (reducing input dimensionality) and balance because it returned better metrics for both the XGBoost and the Logistic Regression. 

When making a decision on wether to use XGBoost or Logistic Regression, I decided to use the XGBoost since it can deal with more complex relations between the features to predict the target. However, we saw that both models returned similar metrics, and Logistic Regression is faster (since it is a simpler model), so one could argue in favor of using Logistic Regression if the inference time was a constraint that we worried about.

### Changes in exploration notebook

- Given a column in the features, the *delay rate* for each value taken by the column is computed as the percentage of delayed flights in that category. [Associated commit](https://github.com/tryolabs/tintin-challenge-tryolabs-latam/commit/bed404d0071cc95a545f29b47477f36a596a314f).

- Minor bugs were fixed,  such as [naming the arguments in `sns.barplot`](https://github.com/tryolabs/tintin-challenge-tryolabs-latam/commit/24487ef5eee651cb23e2c067b8f09f8941558c06), and [boundary cases in the get_period variable not being contemplated](https://github.com/tryolabs/tintin-challenge-tryolabs-latam/commit/4629556eda3db12684e11e30f99fbf129311d9a3).

**REMARKS**

- It has been noticed that the selected top features, are not exactly the ones with greatest importance, since `GRUPO_Copa Air` and `MES_11` are not in the top 10, while `MES_6` and `MES_8` are. However, I have decided not to change those features, since the tests seem to work with the 10 features that were originally used in the exploration notebook, and the README saying 

>**It is not necessary to make improvements to the model**

- I had to change the version of a few libraries in the `requirements.txt` to solve a few conflicts between dependencies.

- It was noticed that the splitting of the data in the notebook was done randomly. That can lead to data leakage, since there can be relations between delayed flights that are close in time (a delay in one flight, can cause delays in following flights). I fixed that in a [now discarded notebook](https://github.com/tryolabs/tintin-challenge-tryolabs-latam/blob/0c1898e5c3b8a9f00d518947908d4b0754eee466/challenge/exploration_all_features.ipynb). The notebook was later discarded because I saw that the tests were still doing a random splitting instead of splitting by time (like using the first 70% of the flights for training and the remaining for testing).
- Some features were never considered when studying feature importance. Some of them are features that were present from the beginning (such as the day of the month, the day of the week, the time, and those regarding the origin and destination of the flight), and some that were generated earlier from these (such as the `high_season` and the `period_day` features). A more thorough study of these features was done (in the [now discarded notebook](https://github.com/tryolabs/tintin-challenge-tryolabs-latam/blob/0c1898e5c3b8a9f00d518947908d4b0754eee466/challenge/exploration_all_features.ipynb) mentioned earlier), where I considered doing one-hot encoding of origin, destination and for the day of the week, and also mapped periodic time variables into a circle (for example the time, the day of the week, the month and the day of the month) using trigonometric functions. 
- I noticed that (before filtering by feature importance), TIPOVUELO was one-hot encoded, eventhough it only takes 2 values ('I' or 'N'). I feel like it makes more sense to only treat it as a single binary column (indicating if it is international or not), instead of the one-hot encoding. I did that change in the [discarded notebook](https://github.com/tryolabs/tintin-challenge-tryolabs-latam/blob/0c1898e5c3b8a9f00d518947908d4b0754eee466/challenge/exploration_all_features.ipynb) mentioned earlier. It is not that important at the end, since after filtering by feature importance you only used the category TIPOVUELO_I.

### Model implementation

- A minor bug regarding changing the type of brackets for `Union` (which should use square brackets instead of curvy brackets) was fixed.
- I selected the XGBoost model with the 'top 10' features and balancing (the scale factor for the balancing is computed inside the fit method instead of just hardcoded, and therefore the model was re initialized in the fit method to have that particular scale factor).
- I also needed to save the trained models, because during tests I had an error saying that it couldn't do predictions since the model was never trained (this will be explained in more detail in the [test section](#test)). I also needed to load the latest trained model in the prediction method whenever we try to do predictions with model that hasn't yet been trained.
- My preprocessing method replaced all the get_dummies that was done to do all the one-hot encodings of the features, because during inference we might need to preprocess inputs that don't have all the values we need (for example, if Copa Air was not present in the input, then I wouldn't be able to get the OPERA_Copa Air feature from a get_dummies).

### Test
- The path to the data in the test had to be changed, since we are running the tests from the main folder of the repository.
- As it was explained before, while testing the prediction method in `test_model_predict`, since that test doesn't run the training method and (for some reason) the model was not keeping the trained version of the model that it got after running the `test_model_fit` test. Therefore, I decided to save the models locally when training in my training method, and to load the most recent version of the model whenever we try to do a prediction with an untrained model in my prediction method.

## Part 2: Deploy model to API
- To do a prediction using the API, I first needed to aggregate the inputs to a single pandas dataframe, preprocess the dataframe, and then run the model to output the predictions.
- A few validation methods were added in the schema classes for the input, in order to verify that the month is between 1 and 12, that the airline is valid (the list of airlines was obtained from all the airlines in our dataset), and to verify that TIPOVUELO is either I (international) or N (national).

No major problems where identified when implementing the API. 

## Part 3: Deploy API to GCP

To deploy our API to GCP, I had to:

1. Fill the Dockerfile
1. Install Google SDK
1. Authentify my Google account
1. Configure docker to use gcloud (with `gcloud auth configure-docker`)
1. Create a project in GCP, which was called `acastro-tryolabs-latam`
1. Build the docker with `docker build -t gcr.io/acastro-tryolabs-latam/flight-predictor . --platform linux/amd64`. The flag `--platform linux/amd64` is there because an error I had when deploying it later, which seems to be a common problem with M1 chips like the one I'm using. The actual error was ` Application failed to start: failed to load /bin/sh: exec format error`, and that flag seems to fix the issue. In the command line to build the docker, you can see that my application was named `flight-predictor`.
1. Push the docker image to gcr, with `docker push gcr.io/acastro-tryolabs-latam/flight-predictor` 
1. Deploy with gcloud: `gcloud run deploy flight-predictor-api --image gcr.io/acastro-tryolabs-latam/flight-predictor --platform managed --region us-central1` 
1. Replace the API's URL (which is `https://flight-predictor-api-emdlm4e4fa-uc.a.run.app/predict`) in the makefile.

Here I needed to change the version of locust in the `requirements-test.txt`, since I needed to use a more recent version of Flask to avoid a couple problems with imports (`cannot import name 'escape' from 'jinja2'` and `cannot import name 'json' from 'itsdangerous'`). This error only ocurred when running the test for this part, but it was solved using a more recent version of locust.

Apart from the tests, I also tested the application by running the command line

```bash
curl -X POST "https://flight-predictor-api-emdlm4e4fa-uc.a.run.app/predict"  -H "Content-Type: application/json" -d '{"flights": [{"OPERA": "Grupo LATAM", "TIPOVUELO": "N", "MES": 3}]}'
```

and it returned the prediction
```bash
{"predict":[0]}
```

## Part 4: CI & CD

In my `cd.yml`, I made use of a couple secret variables, indicating the name of the project (`GCP_PROJECT_ID`) and for my key for my Service Account (`GCP_SA_KEY`). To create the key to my service account, I followed the following steps:

**Navigate to the Service Accounts Page:**
1. Go to the Google Cloud Console.
1. Navigate to "IAM & Admin" > "Service Accounts".
1. Find the existing service account you want to use.

**Create a New Key:**
1. Click on the service account to view its details.
1. Go to the "KEYS" tab.
1. Click on “ADD KEY” and select “Create new key”.
After these steps, a json file containing my GCP_SA_KEY  was downloaded.

Then I added the secret variables to my github repository, I followed the following steps:
1. Go to my repository on GitHub.
1. Click on Settings.
1. Under "Security", click on Secrets & Policies.
1. Click on Actions under "Secrets".
1. Click on "New repository secret".
1. Enter the name (`GCP_PROJECT_ID` or `GCP_SA_KEY`) and their value.
1. Click Add secret.

My continuous integration workflow did the model-test and api-test, while the continuous deployment workflow was concerned about the stress-test.

After seeing that my continuous integration workflow passed the tests (model-test and api-test), I decided to merge my changes, but after that I noticed a few problems with my continuous deployment workflow. 

I had an error during the Run docker build  of the cd.yml, saying `'Unauthenticated request. Unauthenticated requests do not have permission "artifactregistry.repositories.uploadArtifacts" on resource "projects/***/locations/us/repositories/gcr.io" (or it may not exist)'`. To solve this, since I wasn't sure of the main cause of the problem, I did two things:
- Ensured that my GitHub Actions workflow is correctly configured to authenticate with Google Cloud using the service account key. For that, I added in the cd.yml the step `run: gcloud auth configure-docker`
- Made sure the service account associated with the `GCP_SA_KEY` has the necessary permissions. For operations with Google Container Registry, the service account should have the Storage Admin role. To add that role, I followed these steps:
1. Navigate to "IAM & Admin" > "IAM".
1. Find the service account.
1. Click "edit" (pencil icon) to modify its roles.
1. Add the "Storage Admin" role.

Another error I had with my `cd.yml` was that I forgot to install the dependencies (the error said something along the lines of locust: not found). Therefore, I added an step that installs the dependencies in `requirements-test.txt`  (which contains locust).

Finally, the last problem I had was that I needed a trained model that my deployed API was going to use. Therefore, before building the docker container, I added a training step, and I also installed the remaining dependencies that I needed to train my model: 

```
- name: Install dependencies
  run: |
    pip install -r requirements.txt -r requirements-dev.txt -r requirements-test.txt

- name: Train Model
  run: |
    export PYTHONPATH=$PYTHONPATH:$(pwd)
    python3 ./challenge/train.py
```

The training script `./challenge/train.py` used all the data we have for training, and didn't do any splitting between training and test set, since I wasn't concerned about the metrics it returned for the purpose of this challenge.

**REMARKS**:
- There are better ways of dealing with this last problem. Instead of training inside the `cd.yml`, we could have a model registry (using for example, MLflow), and then deploying our API with a model we have available in our model registry. 
- Even though some variables like the project name and the key for my Service Account are treated as secret variables in the repository, I am aware that some variables are still hardcoded (and even the project name which is 'secret', is explicitly mentioned a few times in this markdown documentation just to simplify the exposition). One hardcoded variable is for example `STRESS_URL` in the Makefile, which shouldn't be harcoded. However, I still added a few steps in the `cd.yml` to get the URL to my API when it deploys with gcloud, and uses that URL to run the stress-test.
- After everything worked with the main branch, I modified my `cd.yml` file to handle deployments based on different branches (main, develop, and release/*), by including conditional logic within the deployment steps or create separate jobs for each branch scenario. The current branch you are seeing corresponds to the release/test branch.
