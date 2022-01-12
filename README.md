# Get better
Code for the get better project

## Stage 1
The first stage is an email summariser app. The goal is to relieve the mental effort required to keep up to date with the newsletters that someone is subscribed to.

I imagine the general pattern will be to access a simple webapp, give the app access to your gmail, then it will return a summary to you.

### Step 1: authenticate with gmail
First we have to authenticate with gmail. 

I think the best way to do this is simply to create a small webapp with google login. This will kill two birds with one stone and it just makes sense. Let's follow [this tutorial](https://realpython.com/flask-google-login/).

I'm going to try and take an approach of getting this out ASAP - so trying to not replace any code. Later we can think about what needs to be refactored and changed.

I think this will be a decent approach because that way we can get things done faster instead of spending ages thinking of the "best" way to do things - and it makes it a bit more obvious what pieces are doing what.


Or maybe [this tutorial](https://www.mattbutton.com/2019/01/05/google-authentication-with-python-and-flask/) would be more straightforward since he goes through the google drive API and the app is more bare bones - and doesn't include a database (which will be necessary but isn't really so for now).

#### Django approach / Alternative approach
The other way to do it would be to just build a basic Django app where we solicit permissions once the user is already logged in. I think we should be able to do this (the gmail api seemed to let you do this) - that way we can sort of jump the gun and split up development a bit more, and use something that I'm more familiar with.

Having a look at [this](https://stackoverflow.com/questions/65695786/gmail-api-how-to-simply-authenticate-a-user-and-get-a-list-of-their-messages) and comparing with the flask tutorial I can see that things are almost exactly the same. The key is just to get them to sign in where our app requests the appropriate scopes, and then we "build" the api to access gmail.

I think I got confused by the other post that talked about "server side", where it would be communicating with the API while offline, which is NOT our case.

So what we could do is just do a generic request to the API

#### Back to flask and webserver approach

So for webservers found [this](https://developers.google.com/identity/protocols/oauth2/web-server) via a [github issue](https://github.com/googleapis/google-api-python-client/issues/755)

Note that this explicitly requires us to use something like Flask - and since the flow is overall different to "local" apps, we should follow it.

OK this definitely seems like the best way forward. We are actually asking for a Google login but we don't actually "create" the user here - we just request access (could create the user separately). It seems very simple and is just about properly handling the request.

We can also add code to refresh the token later.

Note that this is a server side handling - we could also handle it on the client side with javascript, if we wanted to. I guess this wouldn't require so many redirects etc.

https://console.cloud.google.com/apis > real first step is to create an API

1. [Enable APIs](https://developers.google.com/identity/protocols/oauth2/web-server#enable-apis):
    * Created a project with aml gmail under learn better
    * Then enable gmail api
2. Create credentials
    * The main thing here is that we have to specify a URI that we redirect to, and for development we use something like `http://localhost:8080` (not sure if we need to add oauth2callback on to it)

Then within the app the general idea is that we need to:

1. Direct the user to authorise (if they need to)
2. Send them through the authorisation flow
3. Save the response we get back in the session
4. Use that response to access the API


OK so everything was quite straightforward:

* Added oauth2callback to the URI in google cloud
* Had to add test users in the consent screen
* It complained that the app was authorised by google - so have to see this later in production

### Step 2: Read emails once authenticated
Now that we have authenticated, have to actually do something to access emails. This will be quite easy as we should just need to "build" the gmail API. The small annoying thing is that we are a bit limited in testing using the flask app - so maybe we should run the [quickstart](https://developers.google.com/gmail/api/quickstart/python) code as well to get used to the API.

Done! The only thing to minorly watch out for was pagination. Note that the API is quite nice to work with and we can insert queries etc.

### Step 3: Improve the UI
So things are quite ugly RN - let's try and gives things a tiny bit of design using some CSS frameworks.

Probably the only thing we need is a standard index page and then something for the summary. Maybe just centre the text somehow. We will do more later when we have more of a summary.

### Step 4: Plan on how to deploy
We don't necessarily want to deploy yet, but let's gather resources on how to do it and what things we need to do.

https://www.thepythoncode.com/article/use-gmail-api-in-python#Searching_for_Emails