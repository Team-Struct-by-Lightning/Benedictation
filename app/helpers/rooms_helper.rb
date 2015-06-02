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

	# each of these cases must return either the json originally passed in from the python server, or a modified version of it reflecting any needed api_type changes and additional attributes such as api_html for rendering wolfram and wiki. This way we don't have to mess with redis or ajax get/posts.
	def choose_api(json)
		json_hash = JSON.parse(json)
		puts "@@@Original hash from python server: " + json_hash['api_type']

		case json_hash['api_type']
		when 'google'
			puts "We will do a google search"
			query(json_hash)
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
			json_hash = schedule_json(json_hash)
			json_hash
		when 'google_docs'
			puts "We will access the google docs api!"
			json_hash #return unmodified json hash
		when 'google_drawings'
			puts "We will access the google drawings api!"
			json_hash #return unmodified json hash
		when 'wolfram'
			puts "We will access the wolfram alpha api!"
			query(json_hash) # returns modified json hash
		when 'wikipedia'
			puts "We will access the wikipedia api!"
			query(json_hash) # returns modified json hash
		else
			json_hash	# In the event of blank queries/no result, return the unmodified hash
		end
	end

	def query_wolfram_alpha(json_hash, order)
		puts "json_hash: ",json_hash.inspect
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
		if doc.xpath("//queryresult").attr("success").to_s == 'false' or doc.xpath("//queryresult").attr("numpods").to_s == '0' or doc.xpath('//*[@title="Definition"]').length != 0
			if json_hash['api_type'] == ""
				if order == "first"
					json_hash['second'] = ""
					json_hash['second' + "_image_name"] = ActionController::Base.helpers.asset_path('wolfram.jpg')
				elsif order == "second"
					json_hash['third'] = ""
					json_hash['third' + "_image_name"] = ActionController::Base.helpers.asset_path('wolfram.jpg')
				else
					json_hash['third'] = ""
					json_hash['third' + "_image_name"] = ActionController::Base.helpers.asset_path('wolfram.jpg')
				end
			else
				json_hash[order] = ""
				json_hash[order + "_image_name"] = ActionController::Base.helpers.asset_path('wolfram.jpg')
			end

		# otherwise the api type is definitely wolfram
		else
			if json_hash['api_type'] == ""
				json_hash['api_type'] = 'wolfram'
				json_hash['first'] = 'wolfram'
				json_hash['first' + "_image_name"] = ActionController::Base.helpers.asset_path('wolfram.jpg')
			else
				# grab the wolfram html
				json_hash[order] = "wolfram"
				json_hash[order + "_image_name"] = ActionController::Base.helpers.asset_path('wolfram.jpg')
			end
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

	def query_wikipedia(json_hash, order)
		query_string = json_hash['noun_phrase'].to_s
		# check if we should change to google search
		if query_string == "" or query_string.nil?
			query_string = json_hash['query'].to_s
		else
			puts "Non-trivial noun phrase found"
		end

		page = Wikipedia.find(query_string)

		if page.content.nil?

			if json_hash['api_type'] == ""
				if order == "first"
					json_hash['second'] = ""
					json_hash['second' + "_image_name"] = ActionController::Base.helpers.asset_path('wikipedia.ico')
				elsif order == "second"
					json_hash['third'] = ""
					json_hash['third' + "_image_name"] = ActionController::Base.helpers.asset_path('wikipedia.ico')
				else
					json_hash['third'] = ""
					json_hash['third' + "_image_name"] = ActionController::Base.helpers.asset_path('wikipedia.ico')
				end
			else
				# grab the wolfram html
				json_hash[order] = ""
				json_hash[order + "_image_name"] = ActionController::Base.helpers.asset_path('wikipedia.ico')
			end


		else
			if json_hash['api_type'] == ""
				json_hash['api_type'] = 'wikipedia'
				json_hash['first'] = 'wikipedia'
				json_hash['first' + "_image_name"] = ActionController::Base.helpers.asset_path('wikipedia.ico')
			else
				# grab the wolfram html
				json_hash[order] = "wikipedia"
				json_hash[order + "_image_name"] = ActionController::Base.helpers.asset_path('wikipedia.ico')
			end
		end
		json_hash
	end

	def query_google(json_hash, order)
		if json_hash['api_type'] == ""
			json_hash['api_type'] = 'google'
			json_hash['first'] = 'google'
			json_hash['first' + "_image_name"] = ActionController::Base.helpers.asset_path('google-fav.jpg')
		else
			# grab the wolfram html
			json_hash[order] = "google"
			json_hash[order + "_image_name"] = ActionController::Base.helpers.asset_path('google-fav.jpg')
		end
		json_hash
	end


	def query(json_hash)
		case json_hash['api_type']
		when 'wolfram'
			json_hash['api_type'] = ""
			json_hash = query_wolfram_alpha(json_hash, 'first')
			json_hash = query_wikipedia(json_hash, 'second')
			json_hash = query_google(json_hash, 'third')
			json_hash
		when 'wikipedia'
			json_hash['api_type'] = ""
			json_hash = query_wikipedia(json_hash, 'first')
			json_hash = query_wolfram_alpha(json_hash, 'second')
			json_hash = query_google(json_hash, 'third')
			json_hash
		when 'google'
			json_hash['api_type'] = ""
			json_hash = query_google(json_hash, 'first')
			json_hash = query_wolfram_alpha(json_hash, 'second')
			json_hash = query_wikipedia(json_hash, 'third')
			json_hash
		end
		json_hash
	end

end
