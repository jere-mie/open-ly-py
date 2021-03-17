# Open-Ly
A simple app simimlar to Bitly, but made for people to easily set up redirects from their domain or a subdomain.
All you need to do is create a `secrets.json` file with the same structure as `secrets-example.json` and fill in the necessary configurations to customize the website to your liking.
Just "pip install" the requirements and run the flask app, and you'll be all set :)
## About some of the files
* `run-example.sh` is an axample script for running the app on a specific port with gunicorn
* `secrets-example.json` is an example of what the `secrets.json` file should look like