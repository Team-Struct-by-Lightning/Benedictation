module ApplicationHelper
	include SessionsHelper

	def get_random_string
		SecureRandom.urlsafe_base64
	end

	 def current_user
    @current_user ||= User.find(session[:user_id]) if session[:user_id]
  end

end