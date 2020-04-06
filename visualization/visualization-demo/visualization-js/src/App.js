import React, { Component } from 'react';
import logo from './logo.svg';
import './App.css';
import Chart from './tree';
import axios from "axios";

class App extends Component {
  // function App() {
  constructor(props) {
    super(props)


  }
  // request document
  handleRequest = () => {
    axios
      .get(`http://localhost:8000/demo/US12345`)
      .then(res => console.log(res))
  }
  render() {
    return (
      <Chart height={1000} width={2000} />
      // <button
      //   onClick={() => this.handleRequest()}>
      //   test
      // </button >
    );
  }
}

export default App;
