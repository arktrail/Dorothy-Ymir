import React, { Component } from "react";
import Tree from "./tree";
import axios from "axios";
import { RenderType } from "./RenderType"
import {cpcCodesDescriptions} from '../cpcCodesDescriptions'
import RenderingTimer from './RenderingTimer'
import { AppBar, TextField, Button, Typography, Slider } from '@material-ui/core';
import {Autocomplete} from '@material-ui/lab';

require('./homepage.css')

const PREDICTED_NODES_MIN = 3
const PREDICTED_NODES_MAX = 9

class HomePage extends Component {
    constructor(props) {
        super(props);
        this.state = {
            text: '',
            cpcCodes: [],
            treeData: null,
            leafNodesNum: PREDICTED_NODES_MIN,
            renderType: RenderType.NOT_RENDER
        };
    }
    // request document
    // handleRequest = () => {
    //     var url = `http://54.163.42.113:8000/demo/US12345`
    //     axios.get(url).then((res) => {
    //         // console.log("handle request get response")
    //         // console.log(res.data)
    //         this.setState({
    //             treeData: res.data,
    //         });
    //     });
    // };

    handleSubmit = () => {
        const {text} = this.state
        var url = `http://54.163.42.113:8000/demo/`
        console.log("handleSubmit")
        this.setState({
            renderType: RenderType.RENDERING
        })

        axios.post(
            url,
            text,
            { headers: { "Content-Type": "text/plain" } }
        ).then((res) => {
            // console.log("handle submit get response")
            // console.log(res.data)
            // console.log(`type of res ${typeof res}`)
            // console.log(`type of res.data ${typeof res.data}`)
            this.setState({
                treeData: { ...res.data },
                renderType: RenderType.RENDERED
            });
        })
    }

    onChangeText(event) {
        this.setState({
            text: event.target.value
        })
    }

    onChangeCPCCodes(event, value) {
        this.setState({
            cpcCodes: value
        })
    }

    onChangePredictedNodesNum(event, value) {
        this.setState({
            leafNodesNum: value,
        });
    }

    createMarks() {
        let marks = [
            {
              value: PREDICTED_NODES_MIN,
              label: PREDICTED_NODES_MIN,
            },
            {
              value: PREDICTED_NODES_MAX,
              label: PREDICTED_NODES_MAX,
            },
        ];
        for (let i = PREDICTED_NODES_MIN + 1; i < PREDICTED_NODES_MAX; i++) {
            marks.push({value: i})
        }
        return marks
    }

    render() {
        console.log("renderType", this.state.renderType)
        const {renderType, treeData, leafNodesNum, text} = this.state
        const marks = this.createMarks()
        
        return (
            <div>
                 {/* header */}
                <AppBar className="header" position="static">
                    <div className="header-container">
                    <div className="header-content">
                        <img className="msaii-logo" src={require('../img/msaii.jpeg')} alt="MSAII" />
                        <div className="dorothy-logo">
                            <img className="header-img" src={require('../img/dorothy-ai-logo.svg')} alt="Dorothy AI" />
                            <div className="d-logo-container">
                                <div className="d-logo-ps">Patent Search</div>
                                <div className="d-logo-s">SIMPLIFIED</div>
                            </div>
                        </div>
                    </div>
                    </div>
                </AppBar>

                {/* main content */}
                <div className="layout">
                    <div className="fixed-body">
                        <div className="main-content">
                            {/* title */}
                            <div className="title">
                                Real-time Patent CPC Codes Classification
                            </div>

                            {/* text input */}
                            <TextField className="text-field" multiline={true} label="Novel Feature"
                                helperText="The distinctive feature that you wish to patent. Required."
                                onChange={this.onChangeText.bind(this)}></TextField>
                            
                            {/* cpc code select */}
                            <Autocomplete
                                multiple
                                options={cpcCodesDescriptions}
                                getOptionLabel={(option) => option.code}
                                onChange={this.onChangeCPCCodes.bind(this)}
                                filterSelectedOptions={true}
                                renderInput={(params) => (
                                <TextField
                                    className="text-field"
                                    {...params}
                                    variant="standard"
                                    label="CPC codes"
                                    helperText="The true subclass level CPC codes for the above content. Optional."
                                />
                                )}
                            />

                            {/* submit button */}
                            <div className="submit-btn-container">
                                {text === '' ?
                                    <Button className="submit-btn" variant="contained" disabled>Submit</Button>
                                    :
                                    <Button className="submit-btn" variant="contained" 
                                    onClick={() => this.handleSubmit()} >Submit</Button>
                                }
                            </div>

                            {/* RENDERING - WAITING FOR RESULT */}
                            {renderType === RenderType.RENDERING && (
                                <RenderingTimer/>
                            )}

                            {/* RENDERED- RESULT RETRIEVED*/}
                            {renderType === RenderType.RENDERED && (
                                <div>
                                    {/*  select leaf node number */}
                                    <Typography className="slider-label" gutterBottom>
                                        Number of predicted subclass-level codes
                                    </Typography>
                                    <Slider
                                        className="slider"
                                        defaultValue={PREDICTED_NODES_MIN}
                                        getAriaValueText={(value) => value}
                                        aria-labelledby="discrete-slider"
                                        valueLabelDisplay="auto"
                                        step={1}
                                        marks={marks}
                                        min={PREDICTED_NODES_MIN}
                                        max={PREDICTED_NODES_MAX}
                                        onChange={this.onChangePredictedNodesNum.bind(this)}
                                    />

                                    {/* TREE GRAPH */}
                                    <div id="tree-graph">
                                        <Tree
                                            treeData={treeData}
                                            height={600}
                                            width={800}
                                            leafNodesNum={leafNodesNum}
                                        />
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                </div> 
            </div>
        );
    }
}

export default HomePage;
