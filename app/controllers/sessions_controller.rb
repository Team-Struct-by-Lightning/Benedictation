class SessionsController < ApplicationController

#this is really weird - why do i need to include this file? it was always auto-included in the sample app
include SessionsHelper

  def create
    user = User.from_omniauth(env["omniauth.auth"])
    log_in user
    redirect_back_or chat_path
  end

  def destroy
    log_out if logged_in?
    redirect_to root_url
  end
end