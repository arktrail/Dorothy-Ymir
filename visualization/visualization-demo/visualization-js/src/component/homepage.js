import React, { Component } from "react";
import Tree from "./tree";
import axios from "axios";
import { RenderType } from "./RenderType"
import { cpcCodesDescriptions } from '../cpcCodesDescriptions'
import RenderingTimer from './RenderingTimer'
import RecallCurve from './RecallCurve'
import DataList from './datalist'
import { AppBar, TextField, Button, Typography, Slider } from '@material-ui/core';
import { Autocomplete } from '@material-ui/lab';
import parse from 'autosuggest-highlight/parse';
import match from 'autosuggest-highlight/match';

require('./homepage.css')

const PREDICTED_NODES_MIN = 1
const PREDICTED_NODES_MAX = 10
const TREE_HEIGHT = 600
const TREE_WIDTH = 800
const DEFAULT_NODES = 3

class HomePage extends Component {
    constructor(props) {
        super(props);
        this.state = {
            text: '',
            cpcCodes: new Set(),
            cpcCodesSubclass: new Set(),
            treeData: null,
            leafNodesNum: DEFAULT_NODES,
            renderType: RenderType.NOT_RENDER,
            descLabels: [],
            descriptionDict: null

        };
    }

    handleSubmit = () => {
        const { text } = this.state
        var url = `http://54.163.42.113:8000/demo/`
        this.setState({
            renderType: RenderType.RENDERING
        })

        axios.post(
            url,
            text,
            { headers: { "Content-Type": "text/plain" } }
        ).then((res) => {
            this.setState({
                treeData: res.data.tree,
                descLabels: res.data.ordered_labels,
                descriptionDict: res.data.description_dict,
                renderType: RenderType.RENDERED
            });
        })
    }

    onChangeText(event) {
        this.setState({
            text: event.target.value
        })
    }

    onChangeCPCCodesV2(event) {
        let values = event.target.value.split(";")
        let cpcCodesSubclass = new Set()
        values.map(i => {
            if (i.length > 0) {
                cpcCodesSubclass.add(i.replace(/\s+/g, '').substring(0, 4))
            }
        })
        this.setState({
            cpcCodesSubclass,
        })
    }


    onChangeCPCCodes(event, value) {
        let cpcCodes = new Set()
        value.map(i => {
            cpcCodes.add(i.code.substring(0, 1));   //  section
            cpcCodes.add(i.code.substring(0, 3));   //  class
            cpcCodes.add(i.code);                   //  subclass
        });
        this.setState({
            cpcCodes,
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
            marks.push({ value: i })
        }
        return marks
    }

    render() {
        const { renderType, treeData, leafNodesNum, text, cpcCodes, cpcCodesSubclass, descLabels, descriptionDict } = this.state
        const marks = this.createMarks()
        return (
            <div>
                {/* header */}
                <AppBar className="header" position="static">
                    <div className="header-container">
                        <div className="header-content">
                            <label className="msaii-label">MSAII</label>
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
                                Real-time Free-Text CPC Codes Classification (Upgraded Version)
                            </div>

                            {/* text input */}
                            <TextField className="text-field" multiline={true} label="Type in the free text to be classified..."
                                // helperText="The distinctive feature that you wish to patent. Required."
                                onChange={this.onChangeText.bind(this)}></TextField>

                            {/* cpc code select */}
                            {/* <Autocomplete
                                multiple
                                autoHighlight={true}
                                options={cpcCodesDescriptions}
                                getOptionLabel={(option) => option.code + '  —————  ' + option.description}
                                onChange={this.onChangeCPCCodes.bind(this)}
                                filterSelectedOptions={true}
                                renderInput={(params) => (
                                    <TextField
                                        className="text-field"
                                        {...params}
                                        variant="standard"
                                        label="CPC codes"
                                    // helperText="The true subclass level CPC codes for the above content. Optional."
                                    />
                                )}
                                renderOption={(option, { inputValue }) => {
                                    const content = option.code + '  —————  ' + option.description
                                    const matches = match(content, inputValue);
                                    const parts = parse(content, matches);

                                    return (
                                        <div className="options">
                                            {parts.map((part, index) => (
                                                <span key={index} style={{ fontWeight: part.highlight ? 700 : 400 }}>
                                                    {part.text}
                                                </span>
                                            ))}
                                        </div>
                                    );
                                }}
                            /> */}

                            {/*  select leaf node number */}
                            {/* <Typography className="slider-label" gutterBottom>
                                Number of predicted subclass-level codes
                            </Typography>
                            <Slider
                                className="slider"
                                defaultValue={PREDICTED_NODES_MIN}
                                // defaultValue={leafNodesNum}
                                getAriaValueText={(value) => value}
                                aria-labelledby="discrete-slider"
                                valueLabelDisplay="auto"
                                step={1}
                                marks={marks}
                                min={PREDICTED_NODES_MIN}
                                max={PREDICTED_NODES_MAX}
                                onChange={this.onChangePredictedNodesNum.bind(this)}
                            /> */}

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
                                <RenderingTimer />
                            )}

                            {/* RENDERED- RESULT RETRIEVED */}
                            {renderType === RenderType.RENDERED && (
                                <div>

                                    {/* cpc code copy past */}
                                    <TextField className="text-field" fullWidth multiline={true} label="Type in the CPC codes for analysis (optional)"
                                        onChange={this.onChangeCPCCodesV2.bind(this)}>
                                    </TextField>

                                    {/* show subclass cpc codes */}
                                    {
                                        cpcCodesSubclass.size !== 0 &&
                                        <div className="subclass">

                                            The Subclass CPC codes parsed are:
                                        {[...cpcCodesSubclass].map(d => (
                                            " " + d + ";"
                                        ))}

                                        </div>
                                    }

                                    {/*  select leaf node number */}
                                    <Typography className="slider-label" gutterBottom>
                                        Number of predicted subclass-level codes
                                    </Typography>
                                    <Slider
                                        className="slider"
                                        defaultValue={DEFAULT_NODES}
                                        // defaultValue={leafNodesNum}
                                        getAriaValueText={(value) => value}
                                        aria-labelledby="discrete-slider"
                                        valueLabelDisplay="auto"
                                        step={1}
                                        marks={marks}
                                        min={PREDICTED_NODES_MIN}
                                        max={PREDICTED_NODES_MAX}
                                        onChange={this.onChangePredictedNodesNum.bind(this)}
                                    />
                                    <div id="tree-graph">
                                        <Tree
                                            treeData={treeData}
                                            height={TREE_HEIGHT}
                                            width={TREE_WIDTH}
                                            leafNodesNum={leafNodesNum}
                                            trueCodeSet={cpcCodes}
                                            trueCodeSetSubclass={cpcCodesSubclass}
                                        />
                                    </div>
                                    <div id="data-list">
                                        <DataList
                                            descriptionDict={descriptionDict}
                                            treeData={treeData}
                                            leafNodesNum={leafNodesNum}
                                            descLabels={descLabels} />
                                    </div>

                                    {cpcCodesSubclass.size !== 0 && descLabels.length !== 0 &&
                                        <div id="recall-curve">
                                            <RecallCurve
                                                height={360}
                                                width={500}
                                                descLabels={descLabels}
                                                trueCodeSet={cpcCodesSubclass}
                                            // trueCodeSet={new Set(['H04B', 'H05K', 'H04W', 'H04L', 'H04M', 'Y02D'])}
                                            />
                                        </div>
                                    }
                                    {/* {cpcCodes.size != 0 && descLabels.length != 0 &&
                                        <div id="recall-curve">
                                            <RecallCurve
                                                height={360}
                                                width={500}
                                                descLabels={descLabels}
                                                trueCodeSet={cpcCodes}
                                            // trueCodeSet={new Set(['H04B', 'H05K', 'H04W', 'H04L', 'H04M', 'Y02D'])}
                                            />
                                        </div>
                                    } */}
                                </div>
                            )}

                        </div>
                    </div>
                    <div className="copyright">
                        &copy; Dorothy AI, CMU MSAII, 2020
                        </div>
                </div>
            </div>
        );
    }
}

export default HomePage;
