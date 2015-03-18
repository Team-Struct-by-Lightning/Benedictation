class StaticPagesController < ApplicationController

  include SessionsHelper

  def home
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
