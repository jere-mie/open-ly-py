# here, 4000 is the port we run on
# the left app is the module we import from
# and the right app is what we run (app.run() at the bottom for example)
gunicorn -b "127.0.0.1:4000" app:app &