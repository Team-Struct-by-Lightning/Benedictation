class RoomsController < ApplicationController

include RoomsHelper

  def room
  	redirect
  	redirect_user
  end

  def api_help
  	json_string = params[:jsonData]
    blah = choose_api(json_string)
    render :json => blah
  end

  # do we need an additional function so that we always get wolfram due to requerying wolfram via
  # the textbox? Or if wiki is better, display a warning and put a wiki link to ask the user if
  # they want to switch?
end
