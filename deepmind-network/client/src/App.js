import React, { Component } from 'react';
import './App.css';
import UsersContainer from './components/UsersContainer';
//import 'bootstrap/dist/css/bootstrap.min.css';

class App extends Component {

    render() {
        document.body.id = '#page-container';
        return (
            <div className="App">
                <div id="content-wrap">
                    <header className="App-header">
                        <h1 className="App-title">~ Völuspá ~</h1>
                    </header>
                    <br />
                    <h3>Users</h3>
                    <hr />
                    <br />
                    <UsersContainer />
                </div>
                <footer className="App-footer">
                    <h2>{'// [GOST] / Ghost Proxy'}</h2>
                </footer>
            </div>
        );
    }
}

export default App;
