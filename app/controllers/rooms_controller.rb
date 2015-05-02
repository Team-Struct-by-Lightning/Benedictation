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

  def get_wolfram
    hash = {}
    hash['result'] = $redis.get("wolfram_html")
    render :json => hash
  end

end
