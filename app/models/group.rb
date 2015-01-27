class Group < ActiveRecord::Base
	has_many :active_relationships, class_name:  "Relationship",
                                  foreign_key: "group_id",
                                  dependent:   :destroy
end
