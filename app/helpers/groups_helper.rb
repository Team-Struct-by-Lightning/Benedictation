module GroupsHelper
	def get_group_id
		url_string = request.original_url
		url_array = url_string.split('/')
		url_index = 0;

		while url_index < url_array.size
			if url_array[url_index] == 'newuser'
				url_index += 1
				break
			end
		url_index += 1
		end

		url_array[url_index]
	end
end
