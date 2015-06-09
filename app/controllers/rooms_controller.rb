class RoomsController < ApplicationController

include RoomsHelper

  def room
  	redirect
  	redirect_user
  end

  def api_help
  	json_string = params[:jsonData]
    return_json= choose_api(json_string)
    render :json => return_json
  end

end
