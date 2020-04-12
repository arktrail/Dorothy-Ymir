import React, { Component } from 'react';
import logo from './logo.svg';
import './App.css';
import Chart from './tree';
import axios from "axios";

class App extends Component {
  // function App() {
  constructor(props) {
    super(props)
    this.state = {
      treeData: null,
      leafNodesNum: 3,
  }

  }
  // request document
  handleRequest = () => {
    axios
      .get(`http://localhost:8000/demo/US12345`)
      .then(res => {
        console.log(res.data)
        this.setState({
          treeData: res.data
        })
      })
  }

  onLeafNodesNumChange(event) {
    this.setState({
      leafNodesNum: event.target.value
    })
  }
  render() {
    return (
      <div>
        {
          this.state.treeData &&
            <Chart treeData={this.state.treeData} height={850} width={2000} />
        }
        Predicted leaf nodes
        <select defaultValue={this.state.leafNodesNum} onChange={this.onLeafNodesNumChange.bind(this)}>
          <option value ={3}>3</option>
          <option value ={6}>6</option>
          <option value ={9}>9</option>
          <option value={12}>12</option>
          <option value={15}>15</option>
        </select>
        <button
          onClick={() => this.handleRequest()}>
          test
        </button >
      </div>
    );
  }
}

export default App;
