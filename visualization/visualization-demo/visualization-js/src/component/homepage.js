import React, { Component } from "react";
import TextField from "./textfield"
import Chart from "./tree";
import axios from "axios";
import { RenderType } from "./RenderType"

class HomePage extends Component {
    // function App() {
    constructor(props) {
        super(props);
        this.state = {
            treeData: null,
            leafNodesNum: 3,
            renderType: RenderType.NOT_RENDER
        };
    }
    // request document
    handleRequest = () => {
        var url = `http://54.163.42.113:8000/demo/US12345`
        axios.get(url).then((res) => {
            // console.log("handle request get response")
            // console.log(res.data)
            this.setState({
                treeData: res.data,
            });
        });
    };

    handleSubmit = (value) => {
        console.log("homepage, handleSubmit ")
        console.log(value)
        var url = `http://54.163.42.113:8000/demo/`
        this.setState({
            renderType: RenderType.RENDERING
        })

        axios.post(
            url,
            value,
            { headers: { "Content-Type": "text/plain" } }
        ).then((res) => {
            console.log("handle submit get response")
            console.log(res.data)
            console.log(`type of res ${typeof res}`)
            console.log(`type of res.data ${typeof res.data}`)
            this.setState({
                treeData: { ...res.data },
                renderType: RenderType.RENDERED
            });
            // this.setState(prevState => ({
            //     treeData: { ...res.data }
            // }));
        })
    }

    onLeafNodesNumChange(event) {
        this.setState({
            leafNodesNum: event.target.value,
        });
    }
    render() {
        console.log("update tree data")
        console.log(this.state.treeData)
        console.log(this.state.renderType)
        return (
            <div>
                <TextField handleSubmit={this.handleSubmit} />
                {/* <TextField type={TextType.PRIOR_ART} /> */}
                {this.state.renderType === RenderType.RENDERING && (
                    <label value={"I am rendering!@"} />
                )}
                {this.state.renderType === RenderType.RENDERED && (
                    <Chart
                        treeData={this.state.treeData}
                        height={850}
                        width={2000}
                        leafNodesNum={this.state.leafNodesNum}
                    />
                )}
        Predicted leaf nodes
                <select
                    defaultValue={this.state.leafNodesNum}
                    onChange={this.onLeafNodesNumChange.bind(this)}
                >
                    <option value={3}>3</option>
                    <option value={6}>6</option>
                    <option value={9}>9</option>
                    <option value={12}>12</option>
                    <option value={15}>15</option>
                    <option value={20}>20</option>
                    <option value={25}>25</option>
                    <option value={30}>30</option>
                </select>
                <button onClick={() => this.handleRequest()}>test</button>
            </div>
        );
    }
}

export default HomePage;
