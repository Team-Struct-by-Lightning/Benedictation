class StaticPagesController < ApplicationController
  require 'etherpad-lite'

  def home
    if logged_in?
      redirect_to chat_path
    end
  end

  def chat
    redirect
  end

  def video
    redirect
  end

  def room
    redirect
    redirect_user
  end

  def icecomm_chat
    redirect
  end

  def giraffe
    redirect
  end

end
