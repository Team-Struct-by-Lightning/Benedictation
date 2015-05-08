module RoomsHelper
	require 'google/api_client'
	require 'json'
	require 'wikipedia'
	require 'net/http'
	require 'open-uri'
	require 'fileutils'
	require 'nokogiri'

	include ScheduleHelper

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

	# each of these cases must return either the json originally passed in from the python server, or a modified version of it reflecting any needed api_type changes and additional attributes such as api_html for rendering wolfram and wiki. This way we don't have to mess with redis or ajax get/posts.
	def choose_api(json)
		json_hash = string_to_json(json)
		puts "@@@Original hash from python server: " + json_hash['api_type']

		case json_hash['api_type']
		when 'google'
			puts "We will do a google search"
			json_hash #return unmodified json hash
		when 'calendar'
			logger.error "We will access the calendar api!"
			json_event = calendar_json(json_hash)
			create_calendar_event(json_event)
			json_hash #return unmodified json hash
		when 'calendar_show'
			logger.error "We will show the calendar"
			#json_event = calendar_show_json(json_hash)
			json_hash #return unmodified json hash 
		when 'schedule_suggest'
			logger.error 'We will find a time that works'
			json_event = schedule_json(json_hash)
			json_hash # return unmodified json hash (for now, EVAN edit this)
		when 'google_docs'
			puts "We will access the google docs api!"
			json_hash #return unmodified json hash
		when 'wolfram'
			puts "We will access the wolfram alpha api!"
			query_wolfram_alpha(json_hash) # returns modified json hash
			# # this code is for testing wikipedia till trevor's done
			# query_wikipedia(json_hash) # returns modified json hash
			# json_hash['api_type'] = 'wikipedia'
			# json_hash
		when 'wikipedia'
			puts "We will access the wikipedia api!"
			query_wikipedia(json_hash) # returns modified json hash
		else
			"NOTHING HAPPENED!?!?!?!?!??!?!??!?!"
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
			json_hash['api_type'] = 'wikipedia'
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
		puts "@@@@@@@@@WIKI@@@@@@@@@@@@@@@@@@" + json_hash['api_html'].to_s
		json_hash
	end

end
