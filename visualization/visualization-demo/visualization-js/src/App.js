import React, { Component } from "react";
import "./App.css";
import HomePage from "./component/homepage"
import UserPage from "./component/userpage"
import axios from "axios";
import {
  BrowserRouter as Router,
  Switch,
  Route,
  Link
} from "react-router-dom";

class App extends Component {
  render() {
    return (
      <Router>
        <div>
          <Switch>
            <Route path="/test">
              <HomePage />
            </Route>
            <Route path="/user">
              <UserPage />
            </Route>
            <Route path="/">
              <HomePage />
            </Route>
          </Switch>
        </div>
      </Router>
    );
  }
}

export default App;
