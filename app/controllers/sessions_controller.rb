class SessionsController < ApplicationController

  def create
    created_user = User.from_omniauth(env["omniauth.auth"])
    create_state
    log_in created_user
    # get list of redis groups associated with the new user: email -> [g1,g2...gn]
    new_group_list = $redis.lrange(created_user.email,0,-1)
    # for each new group, add a new relationship
    new_group_list.each do |group|
        unless Group.where(id: group).empty?
            @new_group_relationship = Relationship.new(user_id:created_user.id, group_id: Group.find_by_id(group).id)
            @new_group_relationship.save
        end
    end
    # clear group list for this email
    $redis.del(created_user.email)
    $redis.del("most_recent_email")
    redirect_back_or chat_path
  end

  def destroy
    log_out if logged_in?
    redirect_to root_url
  end
end