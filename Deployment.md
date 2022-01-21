If you want to deploy it first of all create a database in your localhost using XAMPP and then follow the data.sql file to create the following tables

Then come here in terminal and create a virtual environment usinf the following command 
pyenv local 3.9.6 # I have used python version 3.9.6


pyenv exec python -m venv .venv  #If you dont have pyenv then just use this command  exec python -m venv .venv 


source .venv/Scripts/activate

And then run your app.py file usng command python app.
