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
from google.appengine.api import users #@UnresolvedImport
from google.appengine.ext import webapp as webapp2 #@UnresolvedImport
from google.appengine.ext import db #@UnresolvedImport
from google.appengine.ext.webapp.util import run_wsgi_app #@UnresolvedImport
from jinja2 import Environment, FileSystemLoader
from os.path import join, dirname
import hashlib
import logging
import urllib

# Jinja2 environment to load templates
env = Environment(loader=FileSystemLoader(join(dirname(__file__), 'templates')))

#===============================================================================
# 
#===============================================================================
class Scenario(db.Model):
    '''
    Database of Scenarios 
    '''
    user = db.UserProperty()
    name = db.StringProperty(multiline=False)
    data = db.BlobProperty()
    date = db.DateTimeProperty(auto_now_add=True)

class Rock(db.Model):
    """
    Database of Rocks
    """
    user = db.UserProperty()
    name = db.StringProperty(multiline=False)
    description = db.StringProperty(multiline=True)
    date = db.DateTimeProperty(auto_now_add=True)
    
    vp = db.FloatProperty()
    vs = db.FloatProperty()
    rho = db.FloatProperty()
    
#===============================================================================
# 
#===============================================================================


def get_gravatar_url(email, default=None, size=40):
    '''
    Get the url of this users gravatar 
    '''
    # construct the url
    gravatar_url = "http://www.gravatar.com/avatar/" + hashlib.md5(email.lower()).hexdigest() + "?"
    if default:
        gravatar_url += urllib.urlencode({'s':str(size), 'd':default})
    else:
        gravatar_url += urllib.urlencode({'s':str(size)})
    
    return gravatar_url
    
    
class ModelrPageRequest(webapp2.RequestHandler):
    '''
    Base class for modelr app pages.
    '''
    
    #For the plot server
    # Ideally this should be settable by an admin console.
    HOSTNAME = 'http://localhost:9999'
    
    def rocks(self):
        '''
        return all the rocks this user has saved
        '''
        rocks = Rock.all()
        rocks.filter("user =", users.get_current_user())
        
        return rocks

    def get_base_params(self, user=None, **kwargs):
        '''
        get the default parameters used in base_template.html
        '''
        params = dict(nickname=user.nickname() if user else '',
                      logout=users.create_logout_url(self.request.uri),
                      avatar=get_gravatar_url(user.email()) if user else 'No avatar',
                      HOSTNAME=self.HOSTNAME)
        
        params.update(kwargs)
        
        return params

    def require_login(self):
        '''
        if a user is not logged in then: 
            Send require_login.html and return None
        otherwise:
            return the current user
        '''
        user = users.get_current_user()
        if not user:
            
            template = env.get_template('require_login.html')
            
            template_params = self.get_base_params()
            template_params.update(provider_links={name:users.create_login_url(self.request.uri, federated_identity=uri) for (name, uri) in providers.items()})
            
            html = template.render(template_params)
            
            self.response.out.write(html)
            
        return user


class MainHandler(webapp2.RequestHandler):
    '''
    main page
    '''
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

class RemoveScenarioHandler(webapp2.RequestHandler):
    '''
    remove a scenario from a users db
    '''
    def get(self):
        name = self.request.get('name')
        
        scenarios = Scenario.all()
        scenarios.filter("user =", users.get_current_user())
        scenarios.filter("name =", name)
        scenarios = scenarios.fetch(100)
        
        for scenario in scenarios:
            scenario.delete()
            
        self.redirect('/dashboard')

    
class ModifyScenarioHandler(webapp2.RequestHandler):
    '''
    fetch or update a scenario.
    '''

    def get(self):
        self.response.headers['Content-Type'] = 'application/json'
        name = self.request.get('name')
        
        scenarios = Scenario.all()
        scenarios.filter("user =", users.get_current_user())
        scenarios.filter("name =", name)
        scenarios = scenarios.fetch(1)
        
        logging.info(scenarios[0])
        logging.info(scenarios[0].data)
        if scenarios:
            scenario = scenarios[0]
            self.response.out.write(scenario.data)
        else:
            self.response.out.write('null')
            
        return 
        
    def post(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('All OK!!')

        name = self.request.get('name')
        
        logging.info(('name', name))
        data = self.request.get('json')
        user = users.get_current_user()
        
        logging.info(data)
        scenarios = Scenario.all()
        scenarios.filter("user =", user)
        scenarios.filter("name =", name)
        scenarios = scenarios.fetch(1)
        if scenarios:
            scenario = scenarios[0]
        else:
            scenario = Scenario()
            scenario.user = user
            scenario.name = name
            
        scenario.data = data.encode()
        scenario.put()

class AddRockHandler(webapp2.RequestHandler):
    '''
    add a rock 
    '''
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
    '''
    remove a rock by name.
    '''
    def get(self):
        name = self.request.get('name')
        
        rocks = Rock.all()
        rocks.filter("user =", users.get_current_user())
        rocks.filter("name =", name)
        rocks = rocks.fetch(100)
        
        for rock in rocks:
            rock.delete()
            
        self.redirect('/dashboard')


class ScenarioHandler(ModelrPageRequest):
    '''
    Display the scenario page (uses scenario.html template)
    '''
    def get(self):
        
        self.response.headers['Content-Type'] = 'text/html'
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.headers['Access-Control-Allow-Headers'] = 'X-Request, X-Requested-With'
        
        user = self.require_login()
        if not user:
            return

        template_params = self.get_base_params(user,
                                               rocks=self.rocks().fetch(100))
        
        template = env.get_template('scenario.html')
        html = template.render(template_params)

        self.response.out.write(html)
        
class DashboardHandler(ModelrPageRequest):
    '''
    Display the dashboard page (uses dashboard.html template)
    '''

    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        
        user = self.require_login()
        if not user:
            return
            
        rocks = Rock.all()
        rocks.filter("user =", user)
        rocks.order("-date")

        scenarios = Scenario.all()
        scenarios.filter("user =", user)
        scenarios.order("-date")
        
        for s in scenarios.fetch(100):
            logging.info((s.name, s))
            
        template_params = self.get_base_params(user)
        template_params.update(rocks=rocks.fetch(100),
                               scenarios=scenarios.fetch(100))
        
        
        template = env.get_template('dashboard.html')
        html = template.render(template_params)

        self.response.out.write(html)
            
#Create the web app
app = webapp2.WSGIApplication([('/', MainHandler),
                               ('/dashboard', DashboardHandler),
                               ('/add_rock', AddRockHandler),
                               ('/remove_rock', RemoveRockHandler),
                               ('/scenario', ScenarioHandler),
                               ('/save_scenario', ModifyScenarioHandler),
                               ('/remove_scenario', RemoveScenarioHandler),
                               ],
                              debug=True)


def main():
    run_wsgi_app(app)

if __name__ == "__main__":
    main()
