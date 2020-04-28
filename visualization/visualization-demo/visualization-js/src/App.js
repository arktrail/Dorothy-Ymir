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
  // function App() {
  constructor(props) {
    super(props);
  }
  render() {
    return (
      <Router>
        <div>
          <Switch>
            {/* <Route path="/">
              <HomePage />
            </Route>
            <Route path="/home">
              <HomePage />
            </Route> */}
            <Route path="/users">
              <UserPage />
            </Route>
          </Switch>
        </div>
      </Router>
    );
  }
}

export default App;
