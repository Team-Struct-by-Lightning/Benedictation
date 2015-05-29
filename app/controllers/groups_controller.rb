class GroupsController < ApplicationController

  include GroupsHelper

  skip_before_filter  :verify_authenticity_token

  # redis chat history stuff
  def update_redis
    #append to end of chat history (key = groupname:groupid:chathistory)
    puts params[:redis_key].to_s + ":" + params[:message].to_s
    $redis.rpush(params[:redis_key], params[:message])
    render nothing: true
  end


  def get_redis
      # returns chat history string from redis as array of strings
      chat_history = $redis.lrange(params[:redis_key],0,-1)
      render :json => chat_history
  end

  def get_redis_item
    render :json => $redis.lrange(params[:redis_key],0,-1)[params[:index].to_i]
  end

  def get_redis_length
    hash = {}
    hash['result'] = $redis.lrange(params[:redis_key],0,-1).length
    render :json => hash
  end

  def clear_redis
    $redis.del(params[:redis_key])
    render nothing: true
  end

  def clear_redis_item
    $redis.lrem(params[:redis_key], 0, params[:email])
    render nothing: true
  end

	def show
    @group = Group.find(params[:id])
  end

  def new
    redirect
    @group = Group.new
    @relationship = Relationship.new
  end

  def newuser
    redirect
  end

  def create
    if current_user.nil?
      redirect
    else
      new_group
    end
  end

  def popupadduser
    if current_user.nil?
      redirect
    else
      add_user_to_group
    end
  end



  def destroy
    @group = Group.find_by_name(group_params)
    if @group.destroy
      redirect_to chat_path
    else
      redirect_to chat_path
    end
  end


  private
    def group_params
      params.require(:group).permit(:group_name)
    end

    def popup_group_params
      params.permit(:group_name)
    end

    def set_current_group_params
      params.permit(:group_id)
    end

end
