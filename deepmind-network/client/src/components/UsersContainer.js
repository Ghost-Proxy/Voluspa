import React, { Component } from 'react';
import axios from 'axios';
import User from './User';

class UsersContainer extends Component {
    constructor(props){
        super(props);
        this.state = {
            users: []
        }
    }
    componentDidMount() {
        axios.get('http://localhost:3001/api/v1/users.json')
            .then(response => {
                console.log(response);
                this.setState({
                    users: response.data
                })
            })
            .catch(error => console.log(error))
    }
    render() {
        return (
            <div className="Users-container">
                {this.state.users.map( user => {
                    return (<User user={user} key={user.id} />)
                })}
            </div>
        )
    }
}

export default UsersContainer;