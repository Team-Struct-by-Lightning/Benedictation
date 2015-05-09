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


  # Hey Britt, I haven't thought through this enough but will this
  # hold for concurrency issues?  It seems like we only store one
  # value in Redis here and it is possible if two people try to make
  # the request at the same time, this could return one user's wolfram
  # html to another user.  I could be mistaken here, could you let me know?
  def get_wolfram
    hash = {}
    hash['result'] = $redis.get("wolfram_html").to_s
    render :json => hash
  end

end
