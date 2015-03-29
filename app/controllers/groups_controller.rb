class GroupsController < ApplicationController

  include GroupsHelper

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

end
