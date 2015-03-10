class RelationshipsController < ApplicationController

	def destroy
		groupID = Relationship.find_by_id(params[:id]).group_id

		Relationship.delete(Relationship.find_by_id(params[:id]).group_id)

	  if (Relationship.where(group_id: groupID).empty?)
	  	Group.delete(Group.find_by_id(groupID))
	  end
	  redirect_to chat_path
	end

end
