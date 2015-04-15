module RelationshipsHelper

	def deletes_relationship_and_or_destroys_group
		groupID = Relationship.find_by_id(params[:id]).group_id
		group_name = Group.find_by_id(groupID).group_name

		Relationship.delete(Relationship.where(group_id: groupID, user_id: current_user.id))

	  if (Relationship.where(group_id: groupID).empty?)
	  	# clear the redis keystore for chat/benny history
	  	chat_key = "#{Group.find_by_id(groupID).group_name}:#{groupID}:chathistory"
	  	benny_key = "#{Group.find_by_id(groupID).group_name}:#{groupID}:bennyhistory"
	  	clear_redis(chat_key,benny_key)
	  	# delete the group completely
	  	Group.delete(Group.find_by_id(groupID))
	  	flash[:success] = "You have successfully deleted the group: #{group_name}"
		else
			flash[:success] = "You have successfully left the group: #{group_name}"
	  end
	  redirect_to chat_path
	end

	def clear_redis(chat_history_key, benny_history_key)
    	$redis.del(chat_history_key)
    	$redis.del(benny_history_key)
  end
end
