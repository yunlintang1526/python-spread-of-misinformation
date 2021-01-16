# DSC180A-Project

_Project for the DSC 180A section B02: The Spread of Misinformation Online._


### Requirements to Use:
-----------
- python 3
- install the used modules included in the requirements.txt:
```
pip install -r requirements.txt
```
- In order to rehydrate the twitter data, you need to create a Twitter Developer Api account and get the API(costumer) key, API secret key, Access Token, and Access Token Secret. 
- Save these keys into `.env` file in the project root directory.


### Building the project stages using `run.py`:
-----------
* run **`python run.py data`** for making the dataset
    - By running this command in terminal, the Twitter data (from 03.22 to 08.01 exclusive) will be automatically downloaded in `data/raw`; and the extracted twitter ids and their rehydrated twitter contents will be saved in `data/interim`. All these directories specified in the `config/data-params.json`.
    - The data is sourced from the Panacea Lab Covid19-Twitter Project (https://github.com/thepanacealab/covid19_twitter). This dataset includes tweets acquired from the Twitter Stream related to COVID-19 chatter and it is updated everyday since 03/22.
    - There are three main steps for preparing the data: dowload the raw data for a given valid date (from 2020-03-22 to now), extract tweet ids from the raw data, and finally re-hydrate these ids into twitter contents. All the functions for downloading the data are contained in the folder `src/data/make_dataset.py`. 
* run **`python run.py data analysis`** for analyzing the COVID dataset
    - This will download all the data you need and rehydrated the tweet ids as described above.
    - After downloading, three analysis taks will be performed: 1. Create a list of the top-50 most-used hashtags in the COVID data set; 2. Identify (by guessing) 3 conspiracy or misinformation-related hashtags related to COVID, and 3 "scientific" hashtags. For each, plot the number of occurrences as a function of the date; 3. Create a histogram showing the distribution of number of posts per user.
    - All the plots and data files will be saved in `data/report` as provided in `config/analysis-params`. You can view the result in the notebook which saved in `notebooks/analysis.ipynb`.
* run **`python run.py data analysis feature`** for reporting the features
    - This will automatically download the data and perform the EDA on the data, along with a building feature process. The script of the building feature process is in `src/feature` and the configuration of parameters is in `config/feature-params.json`
    - In the feature process, the user polarities and hashtag polarities will be computed. All results will be saved in `data/report`. The report notebook will be saved in `notebooks/report`.
* run **`python run.py test-data analysis feature`** will perform all targets on test data
    - this command is equivalent to **`python run.py test`**.
    - All the handcrafted test data are saved in `test/testdata`. For ethical and privacy consideration, these data contains no real information of any individual.


### Contributors(Responsibilities):
-----------
* Yunlin Tang: developed code part(data download) for checkpoint 1; formatted the report and developed code part for checkpoint 2.
* Zhou Li: wrote the report part(introduction) for checkpoint 1; wrote the report and helped with writing code for checkpoing 2.