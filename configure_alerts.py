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


class ConfigureAlertsHandler(webapp2.RequestHandler):

  def get(self):
    template = JINJA_ENVIRONMENT.get_template('configure-alerts.html')
    steps_arg = set(self.request.get_all('steps'))
    metric_arg = self.request.get('metric')
    operator_arg = self.request.get('operator')
    threshold_arg = self.request.get('threshold')
    steps = models.DataList.get_by_id('steps').data
    steps = [{'name': step, 'checked': step in steps_arg} for step in steps]
    results = self.CheckRule(steps_arg, metric_arg, operator_arg, threshold_arg)
    params = {
        'steps': json.dumps(steps),
        'results': json.dumps(results),
        'metric': metric_arg,
        'operator': json.dumps(operator_arg),
        'threshold': threshold_arg,
    }
    self.response.write(template.render(params))

  def CheckRule(self, steps_arg, metric_arg, operator_arg, threshold_arg):
    if not steps_arg or not metric_arg or not operator_arg or not threshold_arg:
      return None
    results = []

    masters = models.MasterData.query().fetch()
    for master in masters:
      for step in master.steps:
        if step.name in steps_arg:
          if metric_arg in step.data:
            val = step.data[metric_arg]
            result = {'master': master.key.id(), 'step': step.name, 'data': step.data}
            if operator_arg == '=' and float(val) == float(threshold_arg):
              results.append(result)
            elif operator_arg == '<' and float(val) < float(threshold_arg):
              results.append(result)
            elif operator_arg == '>' and float(val) > float(threshold_arg):
              results.append(result)
    return results
