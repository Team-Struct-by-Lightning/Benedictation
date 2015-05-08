module ScheduleHelper
	require 'json'
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
		user_availability = get_user_availability(json_hash['start']['datetime'],json_hash['end']['datetime'])
		start_range = DateTime.parse(json_hash['start']['datetime'])
		return available_times_json(user_availability, start_range)
	end 

	def get_user_availability(start_str, end_str)
		logger.error "=== In get_available_times ==="

		time_resolution = 30.minutes	# this is a cool Rails thing
		lower_bound = 8
		upper_bound = 17
		tz_offset = "-0700"

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
												'timeMin'	 => start_str + tz_offset,
												'timeMax'	 => end_str + tz_offset,
												'orderBy' 	 => 'startTime',
												'singleEvents' => true})
		events = result.data.items

		start_range = DateTime.parse(start_str)
		end_range   = DateTime.parse(end_str)		
		days = (end_range - start_range).to_i
		userAvailabilityArray = Array.new(days+1) { Array.new(18, true) }

		# Loop over events; fill the corresponding slots in the availability array for each one.
		events.each do |e|
			#logger.error e.summary
			event_start = e.start.dateTime
			event_end   = e.end.dateTime

			# Loop over the days this event covers. (Usually just 1 day)
			day_index = (event_start.to_date - start_range.to_date).to_i
			(event_start.to_date .. event_end.to_date).each do |day|

				day_start = day.to_datetime.change(hour: lower_bound, offset: tz_offset)
				day_end   = day.to_datetime.change(hour: upper_bound, offset: tz_offset)
				stime = [event_start, day_start].max
				etime = [event_end, day_end].min
				# logger.error stime.to_s + " to " + etime.to_s
				time_index = (event_start.to_time - day_start.to_time) / time_resolution	

				# Loop over the time this event covers, in 30 minute increments.
				while stime < etime
					# logger.error "time: " + stime.to_s + ", index: " + time_index.to_s
					userAvailabilityArray[day_index][time_index] = false
					stime += time_resolution
					time_index += 1 
				end
				day_index += 1	
			end	
		end	
		return userAvailabilityArray
	end

	# Create a JSON object representing the times the current user is available, for display purposes
	# This involves converting array indices *back* to datetimes, the reverse of the above.
	# If anyone thinks of a more efficient way let me know
	def available_times_json(availabilityArray, start_range)
		available_times = []
		flag = false
		start_time = start_range
		end_time   = start_range
		availabilityArray.each_with_index do |day, day_index|
			day.each_with_index do |free, time_index|
				if free and not flag
					start_time = (start_range + day_index) + (30*time_index).minutes
					flag = true
				end
				if flag and time_index == 17	# cut off at the end of day
					end_time = (start_range + day_index) + (30*(time_index+1)).minutes
					flag = false
					available_times.append({"start" => start_time, "end" => end_time})
				end
				if not free and flag
					end_time = (start_range + day_index) + (30*time_index).minutes
					flag = false
					available_times.append({"start" => start_time, "end" => end_time})
				end
			end
		end
		return available_times.to_json
	end	

	def create_calendar_event(json)
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
		result = client.execute(:api_method => service.events.insert,
								:parameters => {'calendarId' => 'primary'},
								:body 		=> JSON.dump(json),
								:headers	=> {'Content-Type' => 'application/json'})

		print result.data.id
	end

	def undo_calendar_event(id)
		result = client.execute(:api_method => service.events.delete,
                        		:parameters => {'calendarId' => 'primary', 'eventId' => id})
	end

end