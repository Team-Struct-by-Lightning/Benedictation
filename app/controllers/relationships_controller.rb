class RelationshipsController < ApplicationController

	def destroy
		group = Relationship.find(params[:id]).group_id
	    current_user.remove_relationship(group)
	    redirect_to chat_path    
	end
	
end
