module RoomsHelper
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
			if Relationship.where(group_id: url_array[url_index].to_i, user_id: current_user.id).empty?
				flash[:danger] = 'You are not a member of this group. You must be invited to the group in order to join this room.'
				redirect_to chat_path
			end
		end
	end
end
