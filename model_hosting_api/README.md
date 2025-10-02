### Running

First, set up the environment using the .env file to export all necessary variables:

    export $(grep -v '^#' .env | xargs)

Install all the dependencies with:

    pip install -r requirements.txt

and start with Python from the root of the project (file_hosting_api/):

    python api.py

(please wait a bit for the application to finish loading the model).

### Testing

test.py file contains a test loading a .csv file for inference and cheking the results:

    python test.py