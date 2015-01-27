class CreateGroups < ActiveRecord::Migration
  def change
    create_table :groups do |t|
      t.string :group_name
      t.text :chat_history

      t.timestamps null: false
    end
  end
end
