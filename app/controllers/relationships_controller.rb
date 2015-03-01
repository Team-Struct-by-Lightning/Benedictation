class RelationshipsController < ApplicationController

	def destroy
		group = Relationship.find(params[:id]).group_id

	    current_user.remove_relationship(group)
	  if (Relationship.where(group_id: group.id).empty?)
	  	Group.delete(group_id)
	  end
	  redirect_to chat_path
	end

end
