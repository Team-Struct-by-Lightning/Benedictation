module GroupsHelper
	def get_group_id
		url_string = request.original_url
		url_array = url_string.split('/')
		url_array[-1]
	end

	def get_current_group_name
		id = get_group_id
		Group.find(id).group_name
	end

	def add_user_to_group
		@useremail = params[:newmemberemail]

      if (/\A([\w+\-].?)+@gmail.com$/.match(@useremail)).nil?
        flash.now[:danger] = 'This is not a valid Gmail.  Please check the email again.'
        render 'newuser'
      else
        @user = User.find_by(email: @useremail);
        if @user.nil?
           flash.now[:danger] = 'This user has not joined Benedictation yet.'
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
              flash[:success] = "Added #{User.find(@userid).name} to the group #{Group.find(@curgroupid).group_name}"
              redirect_to chat_path
            else
              flash.now[:danger] = 'Could not add user'
              render 'newuser'
            end
          end
        end
      end
	end
end
