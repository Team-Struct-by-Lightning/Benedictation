module SessionsHelper

	def logged_in?
		!current_user.nil?
	end

	def log_in(user)
    	session[:user_id] = user.id
  	end

  	def log_out
		session.delete(:user_id)
		@current_user = nil
	end

	def current_user?(user)
    	user == current_user
	end

  def redirect_back_or(default)
    redirect_to(session[:forwarding_url] || default)
    session.delete(:forwarding_url)
  end

  def store_location
    session[:forwarding_url] = request.url if request.get?
  end

def current_user
    @current_user ||= User.find(session[:user_id]) if session[:user_id]
  end

end
