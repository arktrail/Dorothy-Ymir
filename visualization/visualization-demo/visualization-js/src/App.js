import React, { Component } from "react";
import "./App.css";
import HomePage from "./component/homepage"
import axios from "axios";

class App extends Component {
  // function App() {
  constructor(props) {
    super(props);
  }
  render() {
    return (
      <div>
        <HomePage />
      </div>
    );
  }
}

export default App;
