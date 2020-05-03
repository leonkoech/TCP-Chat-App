import asyncio
import tornado.escape
import tornado.ioloop
import tornado.locks
import tornado.web
import os.path
import uuid

global_users=[]

class mainhandler(tornado.web.RequestHandler):
    def get(self):
        # create the form for clients to input their usernames
        self.write(
            '<html>'
            '<body>'
            '<form action="/" method="POST">'
            '<input type="text" name="username">'
            '<input type="submit" value="submit">'
            '</form>'
            '</html>'
            )
    # when users submit their usernames get it
    def post(self):
        # check if the user is in the database
        current_username=self.get_body_argument('username')

        if current_username in global_users:
            # if user exists display user exists and a button for going back
            self.write('<h2>user exists<h2><a href="%s"><button>try another</button></a>' % 
                self.reverse_url("home"))
        else:
            #  add the user to the user list
            global_users.append(current_username)
            
            # get the position of the username in the array
            user_position=global_users.index(current_username)
            # redirect the user to  ../user/<position of user in the array>
            self.write('<h2>you have been verified</h2><a href="%s"><button>go to chat</button></a>' %
                   self.reverse_url("user", user_position))
            
class userhandler(tornado.web.RequestHandler):
    def initialize(self, db):
        # If a dictionary is passed as the third element of the URLSpec, 
        # it supplies the initialization arguments which will be passed to 
        # RequestHandler.initialize
        self.db = db

    def get(self, story_id):
        # get the name of current user based on the index received at the header
        # nameofU=global_users[int(story_id)]
        # now render index.html where the chatrooom is and display the cached messages
        self.render("index.html", messages=global_message_buffer.cache)

class MessageBuffer(object):
    def __init__(self):
        # cond is notified whenever the message cache is updated
        self.cond = tornado.locks.Condition()
        self.cache = []
        self.cache_size = 200

    def get_messages_since(self, cursor):
        # Returns a list of messages newer than the given cursor.
        # ``cursor`` should be the ``id`` of the last message received.
        results = []
        # get the messages from the cached messages
        for msg in reversed(self.cache):
            # if message id in the cache matches the id of the last message received
            if msg["id"] == cursor:
                break
            # append/add it to the array results
            results.append(msg)
        results.reverse()
        # now return messages newer than the last message received
        return results

    def add_message(self, message):
        # add message to the cache array
        self.cache.append(message)
        # if the number of items in cache is more than 200
        if len(self.cache) > self.cache_size:
            # remove the first 200 items
            # meaning that when the messages pass 200 they start getting deleted
            self.cache = self.cache[-self.cache_size :]
        self.cond.notify_all()


# Making this a non-singleton is left as an exercise for the reader.
global_message_buffer = MessageBuffer()


class MessageNewHandler(tornado.web.RequestHandler):
    # post a new message to the chat room.

    def post(self):
        if self.get_argument("body")=='USERS \\n':
            # uuid -> universally unique identifiers
            # uuid4 creates a random uuid. uuid1 creates a uuid from a  
            # clients computer network hence not safe
            for item in global_users:
                message = {"id": str(uuid.uuid4()), "body": item+','}
                # beacause the argument has been percent-decoded and is now a byte string,
                # you have to escape to a unicode string
                message["html"] = tornado.escape.to_unicode(
                    # render_string() returns a byte string, which is not supported
                    # in json, so we must convert it to a character string.
                    self.render_string("message.html", message=message)
                )
                # get the button which sits on top of post and has a display of none
                # meaning you are basically chscking if post was clicked
                if self.get_argument("next", None):
                    # and if it was clicked do not redirect the user to /a/message/new as
                    # stated in the form method. Instead ignore it and resirect the user to the current url
                    # bacause tornado has no function to refresh
                    self.redirect(self.get_argument("next"))
                else:
                    # write the message to the screen
                    self.write(message)
                # add the message to chat
                       # open chatlogs file 
                file_object = open('chatlogs.log', 'a')

                # Append username: message to a new line at the end of file
                file_object.write(item+','+'\n')
        
                # Close the file
                file_object.close()
                # add the message to messages
                global_message_buffer.add_message(message)
        else:
            # uuid -> universally unique identifiers
            # uuid4 creates a random uuid. uuid1 creates a uuid from a  
            # clients computer network hence not safe
            message = {"id": str(uuid.uuid4()), "body": self.get_argument("body")}
            # beacause the argument has been percent-decoded and is now a byte string,
            # you have to escape to a unicode string
            message["html"] = tornado.escape.to_unicode(
                # render_string() returns a byte string, which is not supported
                # in json, so we must convert it to a character string.
                self.render_string("message.html", message=message)
            )
            # get the button which sits on top of post and has a display of none
            # meaning you are basically chscking if post was clicked
            if self.get_argument("next", None):
                # and if it was clicked do not redirect the user to /a/message/new as
                # stated in the form method. Instead ignore it and resirect the user to the current url
                # bacause tornado has no function to refresh
                self.redirect(self.get_argument("next"))
            else:
                # write the message to the screen
                self.write(message)
            # open chatlogs file 
            file_object = open('chatlogs.log', 'a')

            # Append username: message to a new line at the end of file
            file_object.write(self.get_argument("body")+'\n')
    
            # Close the file
            file_object.close()
            global_message_buffer.add_message(message)


class MessageUpdatesHandler(tornado.web.RequestHandler):
    # Long-polling request for new messages.
    # Waits until new messages are available before returning anything.
    

    async def post(self):
        # basically getting the message uuid
        cursor = self.get_argument("cursor", None)
        # now get all messages after the current message
        messages = global_message_buffer.get_messages_since(cursor)
        # and if there were no items after the current message run the loop
        while not messages:
            # Save the Future returned here so we can cancel it in
            # on_connection_close.
            self.wait_future = global_message_buffer.cond.wait()
            try:
                # the loop will try to wait 
                await self.wait_future
            # if user cancels the loop by closing the connection
            except asyncio.CancelledError:
                # return nothing
                return
            # else if a message came from waiting, assign it to messages
            messages = global_message_buffer.get_messages_since(cursor)
        if self.request.connection.stream.closed():
            # and if the connection is closed return nothing
            return
        # write the message received to the messages which will be displayed at the screen
        self.write(dict(messages=messages))

    def on_connection_close(self):
        self.wait_future.cancel()
def makeapp():
    url=tornado.web.URLSpec
    #crerate a dictionary that will contain the total number of users
    db=dict()
    # populate this dictionary with dummy data until the total number of users is arrrived at
    for g in range(30):
        db.update({g: g})
    # return the Application object which is responsible for configuration of your app
    return tornado.web.Application([
        # entry point of the app. This is where the client states their username
        url(r'/',mainhandler,name='home'),
        # after the user has stated their name, navigate to a page after they are verified
        # here the user will select whether they want to chat or leave
        # the users can be a maximum of 30
        url(r"/user/([0-30]+)", userhandler, dict(db=db), name="user"),
        (r"/a/message/new", MessageNewHandler),
        (r"/a/message/updates", MessageUpdatesHandler),

    ],
    # generate a random value as the cookie
    cookie_secret="hUmAnsArEwEIrdInmArblE3",
    # set the template path to where the html folder is
    template_path=os.path.join(os.path.dirname(__file__), "templates"),
    # ser the template path to where the css folder is
    static_path=os.path.join(os.path.dirname(__file__), "static"),
    # allow cookies
    xsrf_cookies=False,
    # run in debug mode
    debug=True,
    )

if __name__=='__main__':
    # now make a variable which receives the contents of make app
    app=makeapp()
    # make your app listen to the port that you'll specify
    app.listen(8000)
    # start your app
    tornado.ioloop.IOLoop.current().start()
    