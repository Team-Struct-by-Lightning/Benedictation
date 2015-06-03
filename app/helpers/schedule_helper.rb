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
		attendees.uniq!
		logger.error "@@@@@@@@@@@@ ATTENDEES: " + attendees.to_s
		return attendees
	end

	def calendar_json(json_hash)
		logger.error "@@@ CALENDAR HASH: " + json_hash.inspect

		full_group = json_hash['group_flag']

		if full_group == "True"
			attendee_array = get_attendees()
			attendee_array.map! { |attendee_email| {'email' => attendee_email} }
		else
			attendee_array = current_user.email
		end

		json_event = {
				'summary' => "Meeting scheduled by Benedict",
				'location' => json_hash['location'],
				'start' => {
					'dateTime' => json_hash['start']
					#'timeZone' => 'America/Los Angeles'
				},
				'end' => {
					'dateTime' => json_hash['end']
					#'timeZone' => 'America/Los Angeles'
				},
				'attendees' => attendee_array
		}
	end

	def schedule_json(json_hash)

		start_str = json_hash['start']
		end_str = json_hash['end']
		duration = (json_hash['duration'] || 1.hour).to_i
		time_resolution = (json_hash['time_resolution'] || 30.minutes).to_i
		lower_bound = (json_hash['lower_bound'] || 8).to_i
		upper_bound = (json_hash['upper_bound'] || 17).to_i
		tz_offset = json_hash['tz_offset'] || '-0700'
		nslots = (1.hour / time_resolution) * (upper_bound - lower_bound)

		start_range = DateTime.parse(start_str)
		end_range   = DateTime.parse(end_str)
		days = (end_range - start_range).to_i

		attendees = get_attendees()
		overall_availability = Array.new(days+1) { 2**nslots - 1}
		attendees.each do |attendee_email|
			user_av = get_user_availability(attendee_email, start_str, end_str, lower_bound, upper_bound, time_resolution, tz_offset)
			overall_availability.each_with_index do |x, i|
				overall_availability[i] = x & user_av[i]
			end
		end
		logger.error "overall_availability: " + overall_availability.inspect
		json_hash['suggested_times'] = available_times_json(overall_availability, start_range, duration, time_resolution)
		return json_hash
	end

	# Get the availability for one user as an array of bit vectors.
	def get_user_availability(user_email, start_str, end_str, lower_bound, upper_bound, time_resolution, tz_offset)

		nslots = (1.hour / time_resolution) * (upper_bound - lower_bound)

		client = Google::APIClient.new
		client.authorization.client_id = GoogleAPIKeys["app_id"]
		client.authorization.client_secret = GoogleAPIKeys["secret"]
		client.authorization.scope = "https://www.googleapis.com/auth/calendar"

		user = User.find_by_email(user_email)
		client.authorization.refresh_token = user.refresh_token
		client.authorization.access_token = user.oauth_token
		if client.authorization.refresh_token && client.authorization.expired?
		  client.authorization.fetch_access_token!
		end

		service = client.discovered_api('calendar', 'v3')
		logger.error user_email
		request_body = {:timeMin => start_str,
						:timeMax => end_str,
						:items   => [{:id => user_email}]
					   }
		result  = client.execute(:api_method => service.freebusy.query,
								 :body 		 => JSON.dump(request_body),
								 :headers	 => {'Content-Type' => 'application/json'})

		events = result.data.calendars[user_email].busy

		start_range = DateTime.parse(start_str)
		end_range   = DateTime.parse(end_str)
		days = (end_range - start_range).to_i
		userAvailabilityArray = Array.new(days+1) { 2**nslots - 1}	# Array of Fixnums of 18-bit width

		# Loop over events; fill the corresponding slots in the availability array for each one.
		events.each do |e|
			#logger.error e.summary
			event_start = e.start.getlocal.to_datetime
			event_end   = e.end.getlocal.to_datetime

			# Loop over the days this event covers. (Usually just 1 day)
			day_index = (event_start.to_date - start_range.to_date).to_i
			(event_start.to_date .. event_end.to_date).each do |day|

				day_start = day.to_datetime.change(hour: lower_bound, offset: tz_offset)
				day_end   = day.to_datetime.change(hour: upper_bound, offset: tz_offset)
				stime = [event_start, day_start].max
				etime = [event_end, day_end].min
				#logger.error stime.to_s + " to " + etime.to_s
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
		# userAvailabilityArray.each do |x|
		# 	logger.error "%018b" % x
		# end

		return userAvailabilityArray
	end

	# Create a JSON object representing the times the current user is available, for display purposes
	# Find all contiguous blocks of a given duration.
	# Return a JSON object of the form [{"start": time, "end": time}, {...} ...]
	# 1 IS FREE 0 IS BUSY
	def available_times_json(availabilityArray, start_range, duration, time_resolution)
		available_times = {}
		d = duration / time_resolution
		tr = (time_resolution.to_i) / 60
		availabilityArray.each_with_index do |availability, day|
			day_key = (start_range + day).to_date.to_s
			available_times[day_key] = []
			bits = availability.to_s(2).split("").map {|x| !(x.to_i.zero?) }	# True is free False is busy
			bits.reverse!
			bits.each_with_index do |bit, n|
				if bit and bits[n ... n+d].all?
					start_time = start_range + day + (tr*n).minutes
					end_time = start_range + day + (tr*(n+d)).minutes
					available_times[day_key].append({"start" => start_time, "end" => end_time})
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

		logger.error json
		service = client.discovered_api('calendar', 'v3')
		result = client.execute(:api_method => service.events.insert,
								:parameters => {'calendarId' => 'primary'},
								:body 		=> JSON.dump(json),
								:headers	=> {'Content-Type' => 'application/json'})

		logger.error result.inspect

	end

	def undo_calendar_event(id)
		result = client.execute(:api_method => service.events.delete,
                        		:parameters => {'calendarId' => 'primary', 'eventId' => id})
	end

end