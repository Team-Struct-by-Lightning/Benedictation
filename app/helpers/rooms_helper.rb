module RoomsHelper
	require 'google/api_client'
	require 'json'
	require 'wikipedia'
	require 'net/http'
	require 'open-uri'
	require 'fileutils'
	require 'nokogiri'
	require 'htmlentities'

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

		case json_hash['api_type']
		when 'calendar'
			puts "We will access the calendar api!"
			json_event = calendar_json(json_hash)
			create_calendar_event(json_event)
		when 'calendar_show'
			puts "We will show the calendar"
			json_event = calendar_json(json_hash)
		when 'docs'
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
		#ADD ATTENDEES IN LATER
		# json_hash['attendees'].each do |email|
		# attendee_array << email['email']
		# end
		attendee_array << current_user.email
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

	def query_wolfram_alpha(json_hash)
		coder = HTMLEntities.new
		query_string = json_hash['query'].to_s
		query_string = query_string.split(" " + "\u2018s" + " ").join("s ")
		query_string = query_string.split(" 's ").join("s ")
		puts "&&&&&&&&&&&&&&&&: " + query_string
		app_id = WolframAPIKey["app_id"]
		wolfram_url = URI.parse("http://api.wolframalpha.com/v2/query?appid=P3P4W5-LGWA2A3RU2&input=" + query_string + "&format=image").to_s
		puts "@@@@@@@@@@@@wolfram url: " + wolfram_url
		doc = Nokogiri::XML(open(wolfram_url))
		images = doc.xpath("//img")
		image_array = []
		images.each do |img|
			image_array << img.to_s
			image_array << "<br>"
		end
		imagestring = image_array.join.to_s.split('"').join("'")
		puts  "@@@@@@@@@@@@@@@@@@@@@@@@@@" + imagestring
		#stick in redis
		$redis.set("wolfram_div",imagestring)
		# scripts = doc.xpath("//scripts")
		# puts "@@@@@@@@@@@@@@@@" + scripts.inner_html
		#File.open('wolfram_images.html', 'w') { |file| file.write(imagestring) }






		# doc = Nokogiri::HTML(image_xml.read)
		# markups = []
		# doc.css("markup").each do |markup|
		# 	markup.css("ul").each do |ul|
		# 		ul.content = ""
		# 	end
		# 	markups << markup.inner_html
		# end
		# @wolfram_html = (markups.join("\n").gsub(']]&gt;', '')).gsub('&amp;','&')
		# File.open('blah.html', 'w') { |file| file.write(@wolfram_html) }
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
