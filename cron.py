import models

from google.appengine.api import taskqueue
from google.appengine.api import urlfetch

import json
import logging
import urllib
import webapp2


class UpdateStatsHandler(webapp2.RequestHandler):

  # TODO(sullivan): remove GET
  def get(self):
    taskqueue.add(url='/update-stats', queue_name='UpdateStepData')
    self.response.out.write('Added update-stats task.')

  def log_url_error(self, url, result):
    logging.error('Could not get steps: Response code %s when fetching %s',
                  result.status_code, url)
    self.error(500)

  def post(self):
    url = 'https://chrome-infra-stats.appspot.com/_ah/api/stats/v1/steps'
    result = urlfetch.fetch(url)
    if result.status_code != 200:
      self.log_url_error(url, result)
      return
    steps_data = json.loads(result.content)['steps'][:400]
    steps = models.DataList(id='steps', data=steps_data)
    steps.put()
    step_masters = {}
    for step in steps_data:
      url = ('https://chrome-infra-stats.appspot.com/_ah/api/stats/v1/'
             'steps/%s' % urllib.quote(step))
      result = urlfetch.fetch(url)
      if result.status_code == 200:
        master_list = json.loads(result.content).get('masters')
        master_list = [m['master'] for m in master_list]
        for master in master_list:
          step_masters.setdefault(master, set()).add(step)
    logging.info(step_masters)
    url = 'https://chrome-infra-stats.appspot.com/_ah/api/stats/v1/masters'
    result = urlfetch.fetch(url)
    if result.status_code != 200:
      self.log_url_error(url, result)
      return
    masters_data = json.loads(result.content)['masters']
    masters = models.DataList(id='masters', data=masters_data)
    masters.put()

    for master in masters.data:
      master_entity = models.MasterData.get_or_insert(master)
      url = ('https://chrome-infra-stats.appspot.com/_ah/api/stats/v1'
             '/masters/%s' % urllib.quote(master))
      result = urlfetch.fetch(url)
      if result.status_code != 200:
        self.log_url_error(url, result)
        return
      builder_data = json.loads(result.content)
      builder_data = [builder['name'] for builder in builder_data['builders']]
      master_entity.builders = models.BuilderData(builders=builder_data)
      logging.info('builders: %s', master_entity.builders.builders)
      master_entity.put()
      for step in step_masters.get(master, set()):
        taskqueue.add(url='/update-stats-for-master-step',
                      queue_name='UpdateStepData',
                      params={'master': master, 'step': step})


class UpdateStatsForMasterStepHandler(webapp2.RequestHandler):

  def post(self):
    master = self.request.get('master')
    step = self.request.get('step')
    # TODO(sullivan): These should really be for the last hour, but it's
    # not clear how to deal with timezones--are they all in PST?
    url = ('https://chrome-infra-stats.appspot.com/_ah/api/stats/v1/stats/last'
           '/%s/%s/100' % (urllib.quote(master), urllib.quote(step)))
    result = urlfetch.fetch(url)
    if result.status_code != 200:
      logging.error(('Could not get step data for master %s, step %s: '
                     'Response code %s when fetching %s'),
                    master, step, result.status_code, url)
      if str(result.status_code).startswith('5'):
        self.error(500)
      return
    step_data = json.loads(result.content)
    master = models.MasterData.get_or_insert(master)
    step_property = None
    for cur_step_property in master.steps:
      if cur_step_property.name == step:
        step_property = cur_step_property
        step_property.data = step_data
        break
    if not step_property:
      step_property = models.StepData(name=step, data=step_data)
      master.steps.append(step_property)
    master.put()
