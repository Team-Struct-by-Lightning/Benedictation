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
	result = client.execute(:api_method => service.events.list,
							:parameters => {'calendarId' => 'primary',
											'timeMin'	 => starttime,
											'timeMax'	 => endtime,
											'orderBy' 	 => 'startTime',
											'singleEvents' => true})
	events = result.data.items
	events.each do |e|
		puts e.summary
		puts e.start + " to " + e.end
	end	
end