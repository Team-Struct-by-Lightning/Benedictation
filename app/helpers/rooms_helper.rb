module RoomsHelper
	require 'google/api_client'
	require 'json'
	require 'wikipedia'
	require 'net/http'
	require 'open-uri'
	require 'fileutils'
	require 'nokogiri'
	require 'date'


	GoogleAPIKeys = YAML.load_file("#{::Rails.root}/config/google.yml")[::Rails.env]
	WolframAPIKey = YAML.load_file("#{::Rails.root}/config/wolfram.yml")[::Rails.env]


	def redirect_user
		url_string = request.original_url
		url_array = url_string.split('/')
		url_index = 0;

		while url_index < url_array.size
			if url_array[url_index] == 'room'
				url_index += 1
				break
			end
		url_index += 1
		end

		if url_array[url_index].to_i.to_s == url_array[url_index]
			if Group.where(id: url_array[url_index].to_i, group_name: url_array[url_index + 1]).empty?
				flash[:danger] = 'This group does not exist. Create a group in the sidebar to the left and join its room.'
				redirect_to chat_path
			elsif Relationship.where(group_id: url_array[url_index].to_i, user_id: current_user.id).empty?
				flash[:danger] = 'You are not a member of this group. You must be invited to the group in order to join this room.'
				redirect_to chat_path
			end
		end
	end




##############################################################################################################
##############################################################################################################
##############################################################################################################
##############################################################################################################

																	#API CODE!  ADD STUFF HERE PLEASE

##############################################################################################################
##############################################################################################################
##############################################################################################################
##############################################################################################################


	def string_to_json(json_string)
		puts json_string
		hash = JSON.parse(json_string)
		puts hash
		hash
	end

	def choose_api(json)
		json_hash = string_to_json(json)
		puts json_hash['api_type']

		case json_hash['api_type']
		when 'calendar'
			puts "We will access the calendar api!"
			json_event = calendar_json(json_hash)
			create_calendar_event(json_event)
		when 'calendar_show'
			puts "We will show the calendar"
			#json_event = calendar_show_json(json_hash)
		when 'schedule_suggest'
			puts 'We will find a time that works'
			json_event = schedule_json(json_hash)
		when 'google_docs'
			puts "We will access the google docs api!"
		when 'wolfram'
			# puts "We will access the wolfram alpha api!"
			# query_wolfram_alpha(json_hash)
			query_wikipedia(json_hash)
		when 'youtube'
			puts "We will access the youtube api!"
		when 'wikipedia'
			puts "We will access the wikipedia api!"
			query_wikipedia(json_hash)
		else
			"NOTHING HAPPENED!?!?!?!?!??!?!??!?!"
		end
	end

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

	# def calendar_show_json(json_hash)
	# 	json_show = {
	# 		'summary' => 'Displaying calendar',
	# 		'api_type' => 'calendar_show'
	# 	}
	# end

	def schedule_json(json_hash)

		get_available_times(json_hash['start'],json_hash['end'])

	end

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

	puts '@@@@@@@@@ Entering Schedule Suggest @@@@@@@@@'
	starttime_string = starttime['datetime'] + "-0000"
	endtime_string = endtime['datetime'] + "-0000"
	puts starttime_string, endtime_string
	# This will list all busy times within the week of April 13 - 17
	result = client.execute(:api_method => service.events.list,
                        	:parameters => {'calendarId' => 'primary',
                        					'timeMin' => starttime_string,
                        					'timeMax' => endtime_string })


	events = result.data.items
	#puts result.data.items


	puts "@@@@@@@@@@@@@@@@@@@@@@"
	#starttime = DateTime.parse(starttime)
	#endtime = DateTime.parse(endtime)
	#days = (starttime - endtime)/(60*60*24)

	# Create a boolean array of length (days * 48) if using 30min increments; init all to True (free)
	#event_array = Array.new(days*48, true)
	puts '@@@@@@@@@@ LIST OF EVENTS @@@@@@@@@@@@'
	puts events.length

	events.each do |e|
		puts e
		puts e.start.dateTime , e.end.dateTime, e.summary

		end
	end

	def query_wolfram_alpha(json_hash)
		coder = HTMLEntities.new
		query_string = json_hash['query'].to_s
		query_string = query_string.split(" '").join
		query_string = query_string.split("'").join
		# puts "&&&&&&&&&&&&&&&&: " + query_string
		app_id = WolframAPIKey["app_id"]
		wolfram_url = URI.parse("http://api.wolframalpha.com/v2/query?appid=P3P4W5-LGWA2A3RU2&input=" + URI.encode(query_string.strip) + "&format=html").to_s
		doc = Nokogiri::XML(open(wolfram_url))
		# <queryresult success='false' OR # <pod title='Definition' means we should do wiki instead of wolfram
		api_html = ""
		if doc.xpath("//queryresult").attr("success").to_s == 'false' or doc.xpath('//*[@title="Definition"]').length != 0
			#get wiki hash if any of the above were true
			json_hash = query_wikipedia(json_hash)
			# json_hash['api_type'] = 'wikipedia'
		# otherwise the api type is definitely wolfram
		else
			# grab the wolfram html
			markups = []
			doc.xpath("//markup").each do |markup|
				markups << markup.text
			end
			api_html = markups.join.to_s.split('"').join("'")
			api_html = api_html.split("\n").join()
			json_hash['api_html'] = api_html
		end
		json_hash
	end


	def query_wikipedia(json_hash)
		query_string = json_hash['noun_phrase'].to_s
		# check if we should change to google search
		page = Wikipedia.find(query_string)
		if page.content.nil?
			# need to switch api type to google search
			json_hash['api_type'] = 'google'
		else
			# its definitely wikipedia
			wikipedia_url = URI.parse("https://en.wikipedia.org/wiki/" + URI.encode(query_string.strip) + "?action=render").to_s
			page = Nokogiri::HTML(open(wikipedia_url))
			api_html = page.inner_html.split('"').join("'") # change to using single quotes
			api_html = api_html.split("\n").join() # get rid of newline characters
			json_hash['api_html'] = api_html
		end
		json_hash
		puts "@@@@@@@@@WIKI@@@@@@@@@@@@@@@@@@" + json_hash['api_html'].to_s
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
														:body 			=> JSON.dump(json),
														:headers		=> {'Content-Type' =>
																						'application/json'})

		print result.data.id
	end

	def undo_calendar_event(id)
		result = client.execute(:api_method => service.events.delete,
                        		:parameters => {'calendarId' => 'primary',
                        										'eventId' => id})
	end
end
