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
    hash['result'] = $redis.get("api_html").to_s
    hash['real_api_type'] = $redis.get("real_api_type")
    render :json => hash
  end

end
