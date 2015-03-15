module SessionsHelper

	def logged_in?
		!current_user.nil?
	end

	def log_in(user)
    	session[:user_id] = user.id
  end

  def create_state
    state = get_random_string
    session[:state] = state
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

  def redirect
    if !logged_in?
        store_location
        redirect_to root_url
        flash[:danger] = "Please log in."
    else
    end
  end


end
