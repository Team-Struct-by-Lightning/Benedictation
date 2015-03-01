class GroupsController < ApplicationController
	def show
    @group = Group.find(params[:id])
  end

  def new
    @group = Group.new
    @relationship = Relationship.new

  end

  def create
    @group = Group.new(group_params)    # Not the final implementation!

    if @group.save
      @relationship = Relationship.new(user_id:session[:user_id], group_id:@group[:id])
      if @relationship.save
        # Handle a successful save.
        flash[:success] = "Added the group " + @group.group_name
        redirect_to chat_path
      else
        flash.now[:danger] = 'Invalid group name: Valid group names contain 1-15 valid characters'
        render 'new'
      end
    else
      flash.now[:danger] = 'Invalid group name: Valid group names contain 1-15 valid characters'
      render 'new'
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

end
