module ApplicationHelper

	def get_random_string
		SecureRandom.urlsafe_base64
	end
end