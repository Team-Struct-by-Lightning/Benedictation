class RelationshipsController < ApplicationController

	def destroy
		groupID = Relationship.find_by_id(params[:id]).group_id
		group_name = Group.find_by_id(groupID).group_name

		Relationship.delete(Relationship.where(group_id: groupID, user_id: current_user.id))

	  if (Relationship.where(group_id: groupID).empty?)
	  	Group.delete(Group.find_by_id(groupID))
	  	flash[:success] = "You have successfully deleted the group: #{group_name}"
		else
			flash[:success] = "You have successfully left the group: #{group_name}"
	  end
	  redirect_to chat_path
	end

end
