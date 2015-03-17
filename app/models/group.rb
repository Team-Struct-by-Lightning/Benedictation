class Group < ActiveRecord::Base
	VALID_GROUP_REGEX = /\A\w*\z/
	validates :group_name, presence: true, length: { maximum: 15 }, format: {with: VALID_GROUP_REGEX}
	has_many :active_relationships, class_name:  "Relationship",
                                  foreign_key: "group_id",
                                  dependent:   :destroy

	def Group.new_token
		SecureRandom.urlsafe_base64
	end
end
