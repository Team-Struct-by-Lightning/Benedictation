module ScheduleHelper
	require 'google/api_client'
	require 'date'

	GoogleAPIKeys = YAML.load_file("#{::Rails.root}/config/google.yml")[::Rails.env]

	def calendar_json(json_hash)
		attendee_array = []
		
		full_group = json_hash['group_flag']
		
		if full_group == "True"
			attendee_array = json_hash['attendees_array']
		else
			attendee_array = current_user.email
		end
		
		json_event = {
				'summary' => json_hash['summary'],
				'location' => json_hash['location'],
				'start' => {
					'dateTime' => json_hash['start']['datetime'],
					'timeZone' => json_hash['start']['timezone']
				},
				'end' => {
					'dateTime' => json_hash['end']['datetime'],
					'timeZone' => json_hash['end']['timezone']
				},
				'attendees' => attendee_array
			}
	end

	def schedule_json(json_hash)
		get_available_times(json_hash['start']['datetime'],json_hash['end']['datetime'])
	end 

	def get_available_times(start_str end_str)
		logger.error "=== In get_available_times ==="

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

		result = client.execute(:api_method => service.events.list,
								:parameters => {'calendarId' => 'primary',
												'timeMin'	 => start_str + "-0700",
												'timeMax'	 => end_str + "-0700",
												'orderBy' 	 => 'startTime',
												'singleEvents' => true})
		events = result.data.items


		starttime = DateTime.parse(start_str)
		endtime   = DateTime.parse(end_str)
		duration = (endtime-starttime) / (60*30) # Number of 30m intervals
		free_array = Array.new(true, duration)
		events.each do |e|
			logger.error e.summary
			stime = e.start.dateTime
			etime = e.end.dateTime
			logger.error stime.to_s + " to " + etime.to_s

			# Get the elapsed time between the start/end times and the start of the range in 30m increments
			stime_delta = (stime - starttime) / (60*30)
			etime_delta = (etime - starttime) / (60*30)
			logger.error stime_delta.to_s + " " + etime_delta.to_s


		end	
	end

end