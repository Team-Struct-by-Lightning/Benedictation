class GroupsController < ApplicationController
	def show
    @group = Group.find(params[:id])
  end

  def new
    @group = Group.new
  end

  def create
    @group = Group.new(group_params)    # Not the final implementation!

    if @group.save
      # Handle a successful save.
      flash[:success] = "Added the group " + @group.group_name
      redirect_to chat_path
    else
      render 'new'
    end
  end

  private

    def group_params
      params.require(:group).permit(:group_name)
    end

end
