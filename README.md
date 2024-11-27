### Wizard Battles

This is a small battle game that works using TCP/IP sockets in python.

To run this project, cd to the backend folder and run the server.

*Note: you may have to use `python` or `python3` instead of `py` in the following commands*

```
py server.py
```

The server should start and will say an IP address, make sure to remember it.

Then on any machine on the same internet connection you can open another terminal and run the game.py file

```
py game.py
```

Now, the client will ask for an IP address.
Type in the IP that the server is running on and it should connect and ask you to name your wizard.

To stop the server, simply type `stop` and hit enter in the server terminal.

You can also use `cls` or `clear` to clear the server console.
