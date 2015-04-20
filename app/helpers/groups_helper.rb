module GroupsHelper


  def new_group
    downcase_params = popup_group_params
    downcase_params[:group_name] = downcase_params[:group_name].downcase
    @group = Group.new(downcase_params)    # Not the final implementation!

    if @group.save
      @relationship = Relationship.new(user_id:session[:user_id], group_id:@group[:id])
      if @relationship.save
        # Handle a successful save.
        flash[:success] = "Added the group: " + @group.group_name
        redirect_to chat_path
      else
        flash[:danger] = 'Invalid group name: Valid group names contain 1-15 alpha-numeric and underscore characters'
        redirect_to chat_path
      end
    else
      flash[:danger] = 'Invalid group name: Valid group names contain 1-15 alpha-numeric and underscore characters'
      redirect_to chat_path
    end
  end


	def add_user_to_group
		@useremail = params[:newmemberemail]
    @curgroupid = params[:groupid]

    if (/\A([\w+\-].?)+@gmail.com$/.match(@useremail)).nil?
      flash[:danger] = 'This is not a valid Gmail address.  Please check the email again.'
      redirect_to chat_path
    else
      @user = User.find_by(email: @useremail);
      if @user.nil?
         flash[:danger] = 'This user has not joined Benedictation yet.  An email has been sent to the user on your behalf.'
         # add their email to redis list with email -> [newgroup1, newgroup2...newgroupn]
         $redis.rpush(@useremail.to_s, @curgroupid.to_s)
         # store most recent new email
         $redis.set("most_recent_email", @useremail.to_s)
         redirect_to chat_path
      else
        @userid = @user.id
        @group = Group.find(@curgroupid)
        # check if user already in the group
        if Relationship.find_by(group_id: @curgroupid, user_id: @userid) != nil
          flash[:danger] = 'This user is already a member of this group'
          redirect_to chat_path
        else
          @relationship = Relationship.new(user_id:@userid, group_id:@group[:id])
          if @relationship.save
            # Handle a successful save.
            flash[:success] = "Added #{User.find(@userid).name} to the group #{Group.find(@curgroupid).group_name}"
            redirect_to chat_path
          else
            flash[:danger] = 'Could not add user'
            redirect_to chat_path
          end
        end
      end
    end
	end

end
