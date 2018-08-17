# Semi-Autonomous Trend Detection Using Real-Time Twitter Data


# Setup

Setup for this project is relatively simple. It can be setup on any operating system that has Python3 installed. In this section, it will go through a sample installation using a Google Cloud Engine Instance. The first step for installation is to pull the project from the existing Github repository.

        git pull  https://github.com/dannyoleary1/Final-year-project---Twitter-Analysis-using-Machine-Learning
        
The next step involves setting up a virtual environment. This step is important so that the dependencies of this project can stay separate from the ones stored on the machine. This can potentially become an issue when using different versions. An example of where this happens is if you downloaded this project which uses Django 2.0. Later, you want to update the version of Django to 3.0 (Django 2.0 is the latest at time of writing) and this in turn breaks this project. By installing it with a virtual environment, it ensures Django 2.0 will always be used. The first step of installing a virtual environment is to run the install command from the root directory of the project:

`sudo pip3 install virtualenv`

Next step is to activate the virtual environment:

`source Final-year-project---Twitter-Analysis-using-Machine-Learning/bin/activate`

Now that the virtual environment is installed, it is possible to install all the dependencies that are needed for the project. The requirements.txt contains a list of all the dependencies that are needed by the project:

`pip3 install -r requirements.txt`

Now that all the dependencies are installed, the last steps are setting some of these dependencies up. The first that needs to be done is redis-server. This is needed for Django Channels which is dealing with sending live notifications to the user, and it’s also needed for Celery which is dealing with background tasks.
redis-server
Next up to run is the Celery workers. The celery workers are used for asynchronous background tasks, and the amount set for the concurrency here can vary on the expected amount of traffic. The concurrency parameter sets up a new thread on the machine for parallel processing. There’s 4 different Celery workers that need to be setup:
1.	Default: The default Celery worker is responsible for collecting tweets live and processing them to the relevant Elasticsearch index.
2.	Misc: The misc Celery worker is responsible for running the notifications background task which sends notifications about the latest trends to the user. It runs tasks based on a schedule. One runs every 5 minutes (To detect real time trends), and one at midnight to purge the latest index.
3.	Priority_high: The priority_high Celery worker is responsible for page loads in an asynchronous matter. It shows a loading page until completion and then displayed the actual content. This takes priority over the other queues.
4.	Old_tweets: The old_tweets Celery worked is responsible for collecting old tweets for a specific instance when added or ran individually.
To be ran from the /fyp folder

`nohup celery -A fyp worker –concurrency=15 -Q default -n “default”& > default.out&`

`nohup celery -A fyp worker –concurrency=4 -Q misc -n “misc”& > misc.out&`

`nohup celery -A fyp worker –concurrency=4 -Q priority_high -n “priority_high”& > priority.out&`

`nohup celery -A fyp worker –concurrency=4 -Q old_tweets -n ”old_tweets”&>old.out&`

`nohup celery -A fyp beat &`


Note that nohup is used to keep the commands running outside of SSH and the logs are being outputted to separate files. The last command is responsible for letting Celery know about the schedule.
The last thing that needs to be setup is the server itself. From the root of the project, the settings file needs to be configured:

`cd fyp`

`nano settings.py`

Inside the settings file should be a list called ALLOWED_HOSTS

The IP address of the instance needs to be entered in here. After this, the project is now runnable. From the fyp folder run:

`python3 manage.py runserver 0.0.0.0:8000`

Now all that needs to be done is that a topic needs to be added, and the application will automatically start to detect trends.


