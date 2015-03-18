module GroupsHelper
	def get_group_id
		url_string = request.original_url
		url_array = url_string.split('/')
		url_array[-1]
	end

	def get_current_group_name
		id = get_group_id
		Group.find(id).group_name
	end
end
