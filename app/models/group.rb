class Group < ActiveRecord::Base
	validates :group_name, presence: true, length: { maximum: 15 }
	has_many :active_relationships, class_name:  "Relationship",
                                  foreign_key: "group_id",
                                  dependent:   :destroy

	def Group.new_token
		SecureRandom.urlsafe_base64
	end
end
