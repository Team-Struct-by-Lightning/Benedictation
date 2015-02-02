class Group < ActiveRecord::Base
	validates :group_name, presence: true, length: { maximum: 25 }
	has_many :active_relationships, class_name:  "Relationship",
                                  foreign_key: "group_id",
                                  dependent:   :destroy
end
