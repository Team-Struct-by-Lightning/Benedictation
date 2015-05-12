class RoomsController < ApplicationController

include RoomsHelper

  def room
  	redirect
  	redirect_user
  end

  def api_help
  	json_string = params[:jsonData]
  	choose_api(json_string)
  	render nothing: true
  end

  # this function returns a json object containing the wolfram/wiki html to put in the div, and the augmented api type
  # calculated in rooms_helper wolfram and wiki query methods
  def get_api_html
    hash = {}
    hash['result'] = $redis.get("#{current_user.id}:api_html").to_s
    hash['real_api_type'] = $redis.get("#{current_user.id}:real_api_type")
    render :json => hash
  end


  # do we need an additional function so that we always get wolfram due to requerying wolfram via
  # the textbox? Or if wiki is better, display a warning and put a wiki link to ask the user if
  # they want to switch?
end
