# BetOnYou API

BetOnYou API is a light flask server exposing an API to manage users and related data to fortnite and ClashRoyale. For this purpose you will need your own valid API tokens set inside config.py for those two APIs.
You can get them at the following URLs:
* https://fortniteapi.io/
* https://developer.clashroyale.com/

## Initial setup

First you need to edit the config file at `betOnYou/instance/config.py` to put your API token inside the CLASH_ROYALE_TOKEN and FORTNITE_TOKEN.
Once it is done, go to betOnYou directory then build your docker images using `docker-compose build`
Finally you can start your server by running docker with `docker-compose up`
Congratulations, your app is now running and you can query it.

## Query The API

Now that we have the API we need to have the list of available endpoint.
Here are the public endpoints:

* <your_base_url>/api/players

Get the list of all players recorded inside the DB. Only returns `username`, `email`, `first_name` and `last_name`
```
curl http://127.0.0.1:8080/api/players
{"results":[{"email":"test.test@test.te","first_name":"Test","last_name":"User","username":"test"},{"email":"mister.toto@test.te","first_name":null,"last_name":null,"username":"mister_toto"}]}
```

* <your_base_url>/api/player/<username>

Get the details information for one player given its username. Returns `username`, `email`, `first_name` and `last_name` and specific stored data for fortnite and clash_royale if data stored inside 
```
curl http://127.0.0.1:8080/api/player/test
{"clash_royale":{"loses":68,"trophies":1052,"username":"dragonHS","wins":92},"email":"test.test@test.te","first_name":"Test","fortnite":{"kills":136071,"matches_played":22033,"top1":7715,"username":"Ninja"},"last_name":"Tester","username":"test"}
```
As you can see, we do not return the gamer_tag for either of the game, we only return the public username.

For all the remaining endpoints you will have to add an `Authorisation` header containing a bearer authentication kind with the same token store inside API_SECRET of `config.py`
You can find a postman collection documentation at the following link https://documenter.getpostman.com/view/11795892/Szzoavni?version=latest
