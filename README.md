## KU Polls: Online Survey Questions 

An application to conduct online polls and surveys based
on the [Django Tutorial project](https://docs.djangoproject.com/en/5.1/intro/tutorial01/), with
additional features.

This app was created as part of the [Individual Software Process](
https://cpske.github.io/ISP) course at [Kasetsart University](https://www.ku.ac.th).

## Installation
- clone the repository
```
https://github.com/KhunakornP/Indian-flight-visualizer.git
```
- navigate to the directory
```
cd Indian-flight-visualizer
```
- Install dependencies
```
pip install -r requirements.txt
```
## Running the Application

### How to run the program
1. Create a virtual environment (Optional)
```
python -m venv env
```
2. Activate the virtual environment (Skip if skipping step 1)
```
env/bin/activate

# on windows use
\env\scripts\activate
```
3. Make migrations (If running for the first time)
```
python manage.py migrate
```
4. Load data (If running for the first time)
```
python manage.py loaddata polls/data.json
```
5. Run the server
```
python manage.py runserver
```

## Project Documents

All project documents are in the [Project Wiki](../../wiki/Home).

*Important documents*
- [Vision Statement](../../wiki/Vision%20Statement)
- [Requirements](../../wiki/Requirements)
- [Project Plan](../../wiki/Project%20Plan)
