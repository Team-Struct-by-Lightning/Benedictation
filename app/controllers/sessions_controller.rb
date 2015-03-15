class SessionsController < ApplicationController

include SessionsHelper

  def create
    created_user = User.from_omniauth(env["omniauth.auth"])
    create_state
    log_in created_user
    redirect_back_or chat_path
  end

  def destroy
    log_out if logged_in?
    redirect_to root_url
  end
end