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