# This function gets the available times for the CURRENT USER and puts them in an array. Or something.
# Somehow we are going to have to call this for ALL USERS IN THE ROOM in order to do schedule-suggesting.

require 'datetime'

def get_available_times(starttime, endtime)
	client = Google::APIClient.new
	client.authorization.client_id = GoogleAPIKeys["app_id"]
	client.authorization.client_secret = GoogleAPIKeys["secret"]
	client.authorization.scope = "https://www.googleapis.com/auth/calendar"
	client.authorization.refresh_token = current_user.refresh_token
	client.authorization.access_token = current_user.oauth_token

	if client.authorization.refresh_token && client.authorization.expired?
	  client.authorization.fetch_access_token!
	end

	service = client.discovered_api('calendar', 'v3')

	# This will list all busy times within the week of April 13 - 17
	result = client.execute(:api_method => service.events.freebusy,
							:parameters => {'calendarId' => 'primary',
											'timeMin'	 => starttime,
											'timeMax'	 => endtime})
	events = result.data.calendars

	starttime = DateTime.parse(starttime)
	endtime = DateTime.parse(endtime)
	days = (starttime - endtime)/(60*60*24)

	# Create a boolean array of length (days * 48) if using 30min increments; init all to True (free)
	event_array = Array.new(days*48, true)
	events.busy.each do |e|
		print e.start + " to " + e.end
		# convert its start and end times into ints representing offset from range start in 30m increments
		# (round start down and end up)
		# set all array values between those two (inclusive) to False (not free)
		# you now have an array of when the user is free. now you need one for each user
	end	
end