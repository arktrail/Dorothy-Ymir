import React, { Component } from 'react'
import * as d3 from "d3";

require('./recallCurve.css')
class RecallCurve extends Component {

    constructor(props) {
        super(props);
        this.state = {
            prevData: null,
        };
    }

    componentDidMount() {
        this.createBasics()
        this.draw()
    }

    componentDidUpdate(prevProps) {
        if (this.props.descLabels !== prevProps.descLabels ||
            this.props.trueCodeSet !== prevProps.trueCodeSet) {
                this.draw()
        }
    }

    draw() {
        const data = this.getRecallData()
        this.updateGraph(data)
    }

    getRecallData() {
        const { descLabels, trueCodeSet } = this.props

        let size = 0
        for (let item of trueCodeSet) {
            if(item.length == 4) size += 1
        }

        let data = [{ 'recallAt': 0, 'value': 0 }]
        let count = 0
        for (let i = 0; i < Math.min(descLabels.length, 15); i++) {
            const label = descLabels[i].replace('@','').replace('@','')
            if (trueCodeSet.has(label)) count += 1
            data.push({ 'recallAt': i + 1, 'value': parseFloat(count) / size })
        }
        return data
    }

    createBasics() {
        const { height, width } = this.props
        var margin = { top: 40, right: 150, bottom: 30, left: 50 },
            w = width - margin.left - margin.right,
            h = height - margin.top - margin.bottom;

        const svg = d3.select("#recall-curve")
            .append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("id", "canvas")
            .attr("transform",
                "translate(" + margin.left + "," + margin.top + ")");
    }

    updateGraph(data) {
        const { height, width } = this.props
        // set the ranges
        var x = d3.scaleLinear().range([0, width]);
        var y = d3.scaleLinear().domain([0, 1]).range([height, 0]);

        // Get the data
        const svg = d3.select("#canvas")

        svg.html('')

        // Scale the range of the data
        x.domain(d3.extent(data, function (d) { return d.recallAt; }));
        y.domain(d3.extent(data, function (d) { return d.value; }));

        // draw the path
        svg.append("path")
            .datum(data)
            .attr("class", "line")
            .style("stroke", function () {
                return "#44797B";
            })
            .attr("id", 'tag') // assign ID
            .attr("d", d3.line()
                .curve(d3.curveMonotoneX)
                .x(function (d) { return x(d.recallAt); })
                .y(function (d) { return y(d.value); })
            );

        // Add the scatterplot
        svg.selectAll("dot")
            .data(data)
            .enter().append("circle")
            .attr("class", "point")
            .attr("r", 3)
            .style("stroke-width", 2)
            .style("fill", "rgb(240, 234, 225)")
            .style("stroke", "#44797B")
            .attr("cx", function (d) { return x(d.recallAt); })
            .attr("cy", function (d) { return y(d.value); })

        // Add the X Axis
        svg.append("g")
            .attr("class", "axis")
            .attr("transform", "translate(0," + height + ")")
            .call(d3.axisBottom(x).ticks(5));

        // Add the Y Axis
        svg.append("g")
            .attr("class", "axis")
            .text("Recall Value")
            .call(d3.axisLeft(y).ticks(4));

        // title
        svg.append("text")
            .attr("x", (width / 2))
            .attr("y", -20)
            .attr("text-anchor", "middle")
            .style("font-size", "16px")
            .text("Chart: CPC Codes Recall Curve");

        // x axis
        svg.append("text")
            .attr("x", -20)
            .attr("y", -20)
            .style("font-size", "13px")
            .text("Recall");

        // y axis
        svg.append("text")
            .attr("x", 520)
            .attr("y", 370)
            .style("font-size", "13px")
            .text("Top @");
    }

    render() {
        return <div></div>;
    }
}

export default RecallCurve


