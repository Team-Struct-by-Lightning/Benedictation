module ApplicationHelper
    include SessionsHelper

    def get_random_string
        SecureRandom.urlsafe_base64
    end

    def current_user
        @current_user ||= User.find(session[:user_id]) if session[:user_id]
    end

    def userExists(user_email)
      ( User.find_by_email(user_email).nil? == true ) ? false : true
    end

    def get_most_recent_email
      $redis.get("most_recent_email").to_s
    end

  def user_logged_in(user_id)
  	@user = User.find_by_id(user_id)
  	if @user.nil?
  	elsif @user.logged_in == 1
  		true
  	else
  		false
  	end
  end

  private
  	def update_last_seen
    	current_user.last_seen = DateTime.now
    	current_user.save
  	end

end