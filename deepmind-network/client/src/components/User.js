import React from 'react';

const User = ({user}) =>
    <div className="single-list" key={user.id}>
        <h4>{user.id}</h4>
        <p>{user.discord_id}</p>
        <p>{user.bungie_id}</p>
        <p>{user.destiny_id}</p>
        <p>{user.created_at}</p>
        <p>{user.updated_at}</p>
        <br />
    </div>

export default User;