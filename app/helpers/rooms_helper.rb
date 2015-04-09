module RoomsHelper
	require 'google/api_client'
	require 'json'

	GoogleAPIKeys = YAML.load_file("#{::Rails.root}/config/google.yml")[::Rails.env]

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
		when 'docs'
			puts "We will acess the google docs api!"
		when 'wolfram_alpha'
			puts "We will acess the wolfram alpha api!"
		when 'youtube'
			puts "We will acess the youtube api!"
		when 'wikipedia'
			puts "We will acess the wikipedia api!"
		else
			"NOTHING HAPPENED!?!?!?!?!??!?!??!?!"
		end
	end

	def calendar_json(json_hash)

		attendee_array = []
		json_hash['attendees'].each do |email|
			attendee_array << email['email']
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
