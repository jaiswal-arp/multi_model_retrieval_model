# Assignment05
> [Codelab Slides](https://codelabs-preview.appspot.com/?file_id=14LuhtG4__jyfEC9ih-lwo1A1dE2DT8PUQgLh5-8bMIU/edit#0) <br>
> ----- 

## Index
  - [Objective](#objective)
  - [Project Structure](#project-structure)
  - [How to run the application](#how-to-run-the-application-locally)

  - ----- 

## Objective
This application aims to work on the following use cases by building a multi modal retrieval model 
1. Given an image, will find other images and text tags of similar images <br>
2. Given a text string, find images which match the description of the text string <br>


## Project Structure
```
  ├── qdrant_mm_db                        
  │── images                           # images from the dataset
  │── mixed_images
  │── .gitignore
  │── venv
  │── .env
  │── textapi.py
  │── requirements.txt                  # relevant package requirements file for main
  └── main.py

-------


## How to run the application
- Clone the repo to get all the source code on your machine

```bash
git clone https://github.com/AlgoDM-Fall2023-Team4/Assignment05.git
```

- First, create a virtual environment, activate and install all requirements from the requirements.txt file present
```bash
python -m venv <virtual_environment_name>
```
```bash
source <virtual_environment_name>/bin/activate
```
```bash
pip install -r <path_to_requirements.txt>
```
- Create all the required snowflake resources as per the documentation and also run all the models before proceeding further.

- Add all necessary credentials into a .env file:
```txt
SNOWFLAKE_USERNAME=<snowflake_username>
SNOWFLAKE_PASSWORD=**********
SNOWFLAKE_ACCOUNT_IDENTIFIER=<account_identifier>
SNOWFLAKE_DB=<db_name>
SNOWFLAKE_SCHEMA=<schema_name>
```

- Run the application

```bash
streamlit run streamlit/main.py
