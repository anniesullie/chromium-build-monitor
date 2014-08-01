import models

import json
import logging
import os

from google.appengine.ext import ndb

import jinja2
import webapp2


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__),
                                                'templates')),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class MastersHandler(webapp2.RequestHandler):

  def get(self):
    masters = models.MasterData.query().fetch()
    masters_json = {}
    for master in masters:
      logging.info(master.builders)
      masters_json[master.key.id()] = {
          'steps': dict([(step.name, step.data) for step in master.steps]),
          'builders': master.builders.builders,
      }
    template = JINJA_ENVIRONMENT.get_template('masters.html')
    self.response.write(template.render({
        'masters': json.dumps(masters_json)
    }))


class BuildListHandler(webapp2.RequestHandler):

  def get(self):
    template = JINJA_ENVIRONMENT.get_template('build-list.html')
    self.response.write(template.render({}))
