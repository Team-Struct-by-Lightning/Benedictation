class RelationshipsController < ApplicationController

	include RelationshipsHelper

	def destroy
		deletes_relationship_and_or_destroys_group
	end

end
