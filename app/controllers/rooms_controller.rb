class RoomsController < ApplicationController

include SessionsHelper
include RoomsHelper

  def room
  	redirect
  	redirect_user
  end

end
