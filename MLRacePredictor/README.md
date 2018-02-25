# Machine Learning Race Predictor

This explains a little bit about how this Machine Learning Race Predictor works.

## Data Gathering

There are two scripts responsible for retrieving data from the Garmin connect site. The first one is a python script called [webscraper.py](webscraper.py)

This uses Selenium to parse user running logs that are public and puts the data in data.csv. It also keeps track of all the users that were visited in visited_users.csv

The second script is [garminActivityParser.js](garminActivityParser.js) which runs in node. Now why on earth, I used python for the first script and JavaScript for the second is a little silly. I had in my head that this would all be in python when I started, and then it occurred to me, wait a second, why don't I just do this in JavaScript which I'm more comfortable with since this part isn't the actual machine learning portion. But by the time this occurred to me, I had already gotten pretty far with the first script.

This second script writes data to [goodData.csv](goodData.csv), but ultimtely, I manually copy all of the different runs to [marathonData.csv](marathonData.csv). Why all the moving around and copying? Because, as I was doing this, my scripts weren't so stable and I lost data at some point. So from then on I got paranoid and made backups and moved stuff around.

## Machine Learning

All of the machine learning is in the Jupyter notebook, [MLRacePredictor.ipynb](MLRacePredictor.ipynb). I tried to comment as I went along, but of course the meat of the write up is in the [Capstone Report](report.pdf)