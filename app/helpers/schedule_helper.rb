# TODO: The time range parameters (8:00 AM to 5:00 PM, 30-minute increments) are semi-hardcoded right now,
# especially in the use of 18 as a hardcoded number of timeslots per day. Change this.
# These parameters should be user-specifiable by options on the website.

module ScheduleHelper
	require 'json'
	require 'google/api_client'
	require 'date'

	GoogleAPIKeys = YAML.load_file("#{::Rails.root}/config/google.yml")[::Rails.env]

	# Get the list of all users currently in the room from Redis.
	def get_attendees() 
		url = request.referrer.split("/")	# Get the URL of where the request CAME from, not the url that was requested.
        redis_key = url[-1].to_s + ":" + url[-2].to_s + ":emails";
		attendees = $redis.lrange(redis_key,0,-1)
		logger.error "@@@@@@@@@@@@ ATTENDEES: " + attendees.to_s
		return attendees
	end	

	def calendar_json(json_hash)
		full_group = json_hash['group_flag']
		
		if full_group == "True"
			attendee_array = get_attendees()
			attendee_array.map! { |attendee_email| {'email' => attendee_email} }
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

		start_str = json_hash['start']['datetime']
		end_str = json_hash['end']['datetime']
		start_range = DateTime.parse(start_str)
		end_range   = DateTime.parse(end_str)		
		days = (end_range - start_range).to_i

		# Get the availability array for all users.
		# A spot is free if it's free in ALL attendees (so AND)
		# Implies 1 should be free
		attendees = get_attendees()
		user_availabilities = {}
		overall_availability = Array.new(days+1) { 2**18 - 1}	# Initialize all slots to 1 aka free

		attendees.each do |attendee| 
			user = User.find_by_email(attendee)
			user_availability = get_user_availability(user, start_str, end_str)
			user_availabilities[attendee] = user_availability

			overall_availability.each_with_index do |x, i|
				overall_availability[i] = x & user_availability[i]
			end
		end
		logger.error user_availabilities
		logger.error "Overall availability: " + overall_availability.inspect
		
		# Convert this array to a list of free-time blocks, in JSON format, for returning to the view.x[]
		return available_times_json(overall_availability, start_range)
	end


	### ON BIT VECTORS ###
	# The user availability array is an array of bit vectors, one for each day in the range,
	# each representing the availability for that day.
	# A bit set at position n, on day d, represents the user *busy* on that day at that time index;
	# the time index is the number of [time_resolution]-long intervals since [lower_bound] o'clock.
	# (So, at default values, the number of 30-minute intervals since 8:00:00 AM)
	# With bit vectors, bitvector[0] is the LSB. So the LSB represents 8:00 AM.

	# Get the availability for one user as an array of bit vectors.
	# user: Rails user object
	# start_str: DateTime formatted as string
	# end_str: DateTime formatted as string
	def get_user_availability(user, start_str, end_str)
		logger.error "=== In get_available_times ==="

		time_resolution = 30.minutes	# this is a cool Rails thing
		lower_bound = 8
		upper_bound = 17
		tz_offset = "-0700"

		client = Google::APIClient.new
		client.authorization.client_id = GoogleAPIKeys["app_id"]
		client.authorization.client_secret = GoogleAPIKeys["secret"]
		client.authorization.scope = "https://www.googleapis.com/auth/calendar"

		client.authorization.refresh_token = user.refresh_token
		client.authorization.access_token = user.oauth_token
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
		# userAvailabilityArray = Array.new(days+1) { Array.new(18, true) }
		userAvailabilityArray = Array.new(days+1) { 2**18 - 1}	# Array of Fixnums of 18-bit width

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
					bitmask = 1 << time_index
					userAvailabilityArray[day_index] = userAvailabilityArray[day_index] ^ bitmask
					stime += time_resolution
					time_index += 1 
				end
				day_index += 1	
			end	
		end

		# Make sure the bitwise bullshit is working
		logger.error "===userAvailabilityArray==="
		userAvailabilityArray.each_with_index do |day, day_index|
			logger.error "Day " + day_index.to_s + ": " + day.to_s(2)
		end	

		return userAvailabilityArray
	end

	# Create a JSON object representing the times the current user is available, for display purposes
	# Find all contiguous blocks of a given duration. (Default is 1 hour?)
	# Return a JSON object of the form [{"start": time, "end": time}, {...} ...]
	def available_times_json(availabilityArray, start_range, duration)
		available_times = []
		d = duration / 30.minutes
		availabilityArray.each_with_index do |availability, day|
			bits = availability.to_s(2).split("").map {|x| !x.to_i.zero? }
			bits.each_with_index do |bit, n|
				if bit and bits[n ... n+d].any?
					start_time = (start_range + day) + (30*n).minutes
					end_time = (start_range + day) + (30*(n+1)).minutes
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