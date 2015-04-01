class User < ActiveRecord::Base
  has_many :active_relationships, class_name:  "Relationship",
                                  foreign_key: "user_id",
                                  dependent:   :destroy


  @logged_in = 0

  def log_in
    @logged_in = 1
  end

  def log_out
    @logged_in = 0
  end

  def self.from_omniauth(auth)
    where(provider: auth.provider, uid: auth.uid).first_or_initialize.tap do |user|
      user.provider = auth.provider
      user.uid = auth.uid
      user.name = auth.info.name
      user.email = auth.info.email
      user.oauth_token = auth.credentials.token
      user.oauth_expires_at = Time.at(auth.credentials.expires_at)
      user.refresh_token = auth.credentials.refresh_token
      user.save!
    end
  end


  def remove_relationship(group)
    active_relationships.find_by(group_id: group).destroy
  end

  def refresh_token_if_expired
    if token_expired?
      data = {
        :grant_type => 'refresh_token', :refresh_token => "#{self.refresh_token}",
        :client_id => '165043768486-h54df8d1s3id58p9c603q3cq90pe60it.apps.googleusercontent.com',
        :client_secret => 'fuXwRcqNZAu7iBIqwzAliLx_'
      }
      response    = RestClient.post("https://accounts.google.com/o/oauth2/token", data)
      refreshhash = JSON.parse(response.body)
      #token_will_change!
      #expiresat_will_change!
      self.oauth_token = refreshhash['access_token']
      self.oauth_expires_at = DateTime.now + refreshhash["expires_in"].to_i.seconds
      self.save
      #puts 'Saved'
    end
  end

  def token_expired?
    expiry = Time.at(self.oauth_expires_at)
    if expiry < Time.now
      return true
    else
      return false
    end# expired token, so we should quickly return
  end

end