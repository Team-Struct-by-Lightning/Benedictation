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
			json_event = calendar_json(json_hash)
		when 'schedule_suggest'
			puts 'We will find a time that works'
			json_event = schedule_json(json_hash)
		when 'google_docs'
			puts "We will access the google docs api!"
		when 'wolfram'
			puts "We will access the wolfram alpha api!"
			query_wolfram_alpha(json_hash)
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
		puts "&&&&&&&&&&&&&&&&: " + query_string
		app_id = WolframAPIKey["app_id"]
		wolfram_url = URI.parse("http://api.wolframalpha.com/v2/query?appid=P3P4W5-LGWA2A3RU2&input=" + URI.encode(query_string.strip) + "&format=html,image").to_s
		puts "@@@@@@@@@@@@wolfram url: " + wolfram_url
		doc = Nokogiri::XML(open(wolfram_url))
		markups = []
		doc.xpath("//markup").each do |markup|
			markups << markup.text
		end

		wolfram_html = markups.join.to_s.split('"').join("'")
		wolfram_html = wolfram_html.split("\n").join()
		puts "@@@@@@@@@@@@@@@@@@@html" + wolfram_html
		

		$redis.set("wolfram_html",wolfram_html.to_s)



	end


	def query_wikipedia(json_hash)

		page = Wikipedia.find( json_hash['query'] )

		wiki_hash = Hash.new
		wiki_hash['title'] = page.title
		wiki_hash['content'] = page.content
		wiki_hash['categories'] = page.categories
		wiki_hash['links'] = page.links
		wiki_hash['extlinks'] = page.extlinks
		wiki_hash['images'] = page.images
		wiki_hash['image_urls'] = page.image_urls
		wiki_hash['image_descriptionurls'] = page.image_descriptionurls
		wiki_hash['coordinates'] = page.coordinates
		wiki_hash['templates'] = page.templates

		puts wiki_hash
		wiki_hash
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
