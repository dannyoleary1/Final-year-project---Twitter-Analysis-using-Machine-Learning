# Twitter Analysis using Machine Learning

## Twitter API
Using the Twitter API to collect a series of tweets that can be configured in a config file. This can be used to collect whatever type of tweets as live data for whatever search query you want. For example this can be done to collect tweets on “Security Breaches” which should give back the latest tweets for “Security Breaches”. The data can be stored using ElasticSearch when aggregated or to a JSON file for later processing. 

## Data Pre-Processing with Python, NLTK and Pandas
When the data has been collected using either ElasticSearch or a JSON file, the next step is to pre process the data. This will involve getting the data into the right format for analysis with TensorFlow. NLTK is a python library that will be important for this since this will be used to process the tweets into a more managable format. It could filter out for example specific characters or emoji’s. Pandas may also be useful in this to make the tweets into a more managable format for analysis.

## Type of Analysis
The plan for this is to carry out analysis on tweets that are very generic and could potentially cause issues with Machine Learning aspects. Some of the ideas I have for this are to be able to do analysis to detect new activities from the tweets collected, an example of this would be being able to see when security breaches have just happened based on the new activity in tweets. For further analysis, I plan to do sentiment analysis to see if the tweets are either positive or negative. ADD MORE?

## Supervised or Unsupervised Learning
When using Machine Learning techniques, it will be important to distinguish between doing analysis on supervised or unsupervised learning. For this I plan on giving the option for both, so a user can pick if there data is labelled or not. Semi-Supervised may also be supported.

## Tensorflow for analysis
Using tensorflow as the library for Machine Learning. This will be responsible for taking the data after it has been pre-processed and performing the analysis on it. This will need to support many different algorithms and supervised, unsupervised, and semi-supervised learning mechanisms to do so. 

## Django as a web application framework
Django will be used as the web application framework and will be responsible for providing a place to view all the analysis that has been carried out. The breakdown of this will be discussed further below just as a blueprint to aim for.



List of current technologies that need to be installed. This will be updated as I go and also will include installation links:
Django
Python3
Tensorflow
NLTK
ElasticSearch/Elasticpy
Jquery
