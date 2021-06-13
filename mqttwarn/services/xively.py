from builtins import str
import xively
import datetime
import requests


def get_datastream(feed, datastream_name):
	try:
		for d in feed.datastreams:
			if d.id == datastream_name:
				return d

		#Strange ... lets explicitly request the datastream
		datastream = feed.datastreams.get(datastream_name)
		return datastream
	except:
		#Ho! we didn't find the datastream, better create him myself
		datastream = feed.datastreams.create(datastream_name)
		return datastream


def plugin(srv, item):
	srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

	config = item.config

	#it's essential to have an apikey
	if type(config) != dict or 'apikey' not in config or not config['apikey']:
		return False

	api = xively.XivelyAPIClient(config['apikey'])


	feed = api.feeds.get(int(item.target))
	now = datetime.datetime.utcnow()

	#lets filter data
	ds = []
	for k,v in list(item.data.items()):
		if k in item.addrs:
			ds.append(xively.Datastream(id=str(k), current_value=str(v), at=now))
	feed.datastreams = ds

	#all set, lets update back to xively
	try:
		feed.update()
	except requests.HTTPError as e:
		srv.logging.error("Xively Error: " + e.strerror)
	return True
