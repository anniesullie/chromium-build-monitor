import webapp2
import configure_alerts
import cron
import masters

URLS = [
  ('/update-stats', cron.UpdateStatsHandler),
  ('/update-stats-for-master-step', cron.UpdateStatsForMasterStepHandler),
  ('/masters', masters.MastersHandler),
  ('/build-list', masters.BuildListHandler),
  ('/configure-alerts', configure_alerts.ConfigureAlertsHandler),
]

APPLICATION = webapp2.WSGIApplication(URLS, debug=True)
