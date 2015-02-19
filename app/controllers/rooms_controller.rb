class RoomsController < ApplicationController

include SessionsHelper

  def room
    if !logged_in?
      store_location
      redirect_to root_url
      flash[:danger] = "Please log in."
    else

    end
  end
end
