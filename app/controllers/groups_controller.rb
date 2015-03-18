class GroupsController < ApplicationController
  include SessionsHelper
  include GroupsHelper

	def show
    @group = Group.find(params[:id])
  end

  def new
    @group = Group.new
    @relationship = Relationship.new
  end

  def redirect_function
    redirect
  end

  def create
    @group = Group.new(group_params)    # Not the final implementation!

    if @group.save
      @relationship = Relationship.new(user_id:session[:user_id], group_id:@group[:id])
      if @relationship.save
        # Handle a successful save.
        flash[:success] = "Added the group: " + @group.group_name
        redirect_to chat_path
      else
        flash.now[:danger] = 'Invalid group name: Valid group names contain 1-15 alpha-numeric or underscore characters'
        render 'new'
      end
    else
      flash.now[:danger] = 'Invalid group name: Valid group names contain 1-15 alpha-numeric or underscore characters'
      render 'new'
    end
  end

  def adduser
    # check if user exists in benedictation

    @useremail = params[:newmemberemail]
    @user = User.find_by(email: @useremail);

    if @user.nil?
       flash.now[:danger] = 'This user has not joined Benedictation yet'
       render 'newuser'
    else
      @userid = @user.id
      @curgroupid = get_group_id
      @group = Group.find(@curgroupid)
      # check if user already in the group
      if Relationship.find_by(group_id: @curgroupid, user_id: @userid) != nil
        flash.now[:danger] = 'User is already part of this group'
        render 'newuser'
      else
        @relationship = Relationship.new(user_id:@userid, group_id:@group[:id])
        if @relationship.save
          # Handle a successful save.
          flash[:success] = "Added the user: #{params[:newmemberemail]}"
          redirect_to chat_path
        else
          flash.now[:danger] = 'Could not add user'
          render 'newuser'
        end
      end
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
