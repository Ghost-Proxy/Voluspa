class CreateUsers < ActiveRecord::Migration[6.0]
  def change
    create_table :users do |t|
      t.string :discord_id
      t.string :bungie_id
      t.string :destiny_id

      t.timestamps
    end
  end
end
