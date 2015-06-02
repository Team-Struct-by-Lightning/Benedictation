class GroupsController < ApplicationController

  require 'json'
  require 'open-uri'
  require 'nokogiri'
  WolframAPIKey = YAML.load_file("#{::Rails.root}/config/wolfram.yml")[::Rails.env]

  include GroupsHelper

  skip_before_filter  :verify_authenticity_token

def get_wolfram_html
      query = params[:query]
      query = query.to_s
      query = query.split(" '").join
      query = query.split("'").join
      app_id = WolframAPIKey["app_id"]
      wolfram_url = URI.parse("http://api.wolframalpha.com/v2/query?appid=P3P4W5-LGWA2A3RU2&input=" + URI.encode(query.strip) + "&format=html").to_s
      doc = Nokogiri::XML(open(wolfram_url))
      markups = []
      doc.xpath("//markup").each do |markup|
        markups << markup.text
      end
      api_html = markups.join.to_s.split('"').join("'")
      api_html = api_html.split("\n").join()
      hash = {}
      hash['result'] = api_html
      render :json => hash
    end

  # redis chat history stuff
  def update_redis
    #append to end of chat history (key = groupname:groupid:chathistory)
    # logger.error params[:redis_key].to_s + ":" + params[:message].to_s
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

  def get_redis_item_name
    json = $redis.lrange(params[:redis_key],0,-1)[params[:index].to_i]
    json = JSON.parse(json)
    json['user_name'] = params[:user_name]
    puts json
    render :json => json
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

  def update_unique_benny_query_history
    $redis.set(params[:query], params[:value])
    render nothing: true 
  end

  def get_unique_benny_query
    hash = {}
    api_json = $redis.get(params[:query])
    if api_json.nil?
      hash['result'] = api_json.to_s
    else
      hash['result'] = api_json
    end
    render :json => hash
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
