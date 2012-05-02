#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import logging
from google.appengine.api import users
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.ext import db

# import code for encoding urls and generating md5 hashes
import urllib, hashlib
import os


class RockModels(db.Model):
    user = db.UserProperty()
    uri = db.StringProperty(multiline=False)

class Rock(db.Model):
    """Models an individual Rock"""
    user = db.UserProperty()
    name = db.StringProperty(multiline=False)
    description = db.StringProperty(multiline=True)
    date = db.DateTimeProperty(auto_now_add=True)
    
    vp = db.FloatProperty()
    vs = db.FloatProperty()
    rho = db.FloatProperty()



def get_gravatar_url(email, default="http://agilemodelr.appspot.com/default.jpg", size=40):

    # construct the url
    gravatar_url = "http://www.gravatar.com/avatar/" + hashlib.md5(email.lower()).hexdigest() + "?"
    gravatar_url += urllib.urlencode({'s':str(size)})
    
    return gravatar_url
    
class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.redirect('/dashboard')

providers = {
    'Google'   : 'www.google.com/accounts/o8/id', # shorter alternative: "Gmail.com"
    'Yahoo'    : 'yahoo.com',
    'MySpace'  : 'myspace.com',
    'AOL'      : 'aol.com',
    'MyOpenID' : 'myopenid.com'
    # add more here
}

class AddRockHandler(webapp2.RequestHandler):
    def get(self):
        name = self.request.get('name')
        
        rocks = Rock.all()
        rocks.filter("user =", users.get_current_user())
        rocks.filter("name =", name)
        rocks = rocks.fetch(1)
        
        if rocks:
            rock = rocks[0]
        else:
            rock = Rock()
            rock.user = users.get_current_user()
            rock.name = self.request.get('name')
            
        rock.vp = float(self.request.get('vp'))
        rock.vs = float(self.request.get('vs'))
        rock.rho = float(self.request.get('rho'))
            
        rock.put()
        
        self.redirect('/dashboard')

class RemoveRockHandler(webapp2.RequestHandler):
    def get(self):
        name = self.request.get('name')
        
        rocks = Rock.all()
        rocks.filter("user =", users.get_current_user())
        rocks.filter("name =", name)
        rocks = rocks.fetch(100)
        
        for rock in rocks:
            rock.delete()
            
        self.redirect('/dashboard')


class LoginHandler(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        
        user = users.get_current_user()
        if not user:
            self.response.out.write('Hello world! Sign in at: ')
            for name, uri in providers.items():
                self.response.out.write('[<a href="%s">%s</a>]' % (users.create_login_url(self.request.uri, federated_identity=uri), name))
            return
        
        rocks = Rock.all()
        
        logging.info(str([(rock.name, rock.user) for rock in rocks.fetch(100)]))
        
        logging.info(str(users.get_current_user()))
        
        rocks.filter("user =", users.get_current_user())
        rocks.order("-date")
        
        logging.info(str([(rock.name, rock.user) for rock in rocks.fetch(100)]))
        
        gurl = get_gravatar_url(user.email())
        
        path = os.path.join(os.path.dirname(__file__), 'templates', 'dashboard.html')
        template_params = dict(nickname=user.nickname(), logout=users.create_logout_url(self.request.uri), avatar=gurl,
                               rocks=rocks.fetch(100))
        
        html = template.render(path, template_params)

        self.response.out.write(html)
            

app = webapp2.WSGIApplication([('/', MainHandler),
                               ('/dashboard', LoginHandler),
                               ('/add_rock', AddRockHandler),
                               ('/remove_rock', RemoveRockHandler),
                               ],
                              debug=True)


def main():
    run_wsgi_app(app)

if __name__ == "__main__":
    main()
