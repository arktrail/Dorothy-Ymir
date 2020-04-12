import * as d3 from "d3";
import React, { Component } from 'react';
import './tree.css';
// import { treePredictedData, treeTrueData } from './data'
import { selector } from "d3";

const circleColor = "#FB9A0D";
const trueCircleColor = "#ff3b00";

// var link_weight = d3.scale.linear()
//                     .domain([0, 100])
//                     .range([0, 100]);

// TTD:
// 2. add dot link lines for true-not-predicted node : x
// 3. add different color node for true-predicted node : x
// 1. add button to choose how many nodes I need to render
// 5. change the font size : x
// 6. add labels to 

function isTrueNotPredicted(d) {
    console.log(d)
    console.log("is true and not predicted")
    return d.data.true === true && d.data.prob === -1;
}

function isFalseButPredicted(d) {
    console.log(d)
    console.log("is false but predicted")
    return d.data.true === false && d.data.prob !== -1;
}

function isTrueAndPredicted(d) {
    console.log(d)
    console.log("is true and predicted")
    return d.data.true === true && d.data.prob !== -1;
}

function descriptionIndent(d) {
    switch (d.data.level) {
        case "SECTION":
            return "|--";
        case "CLASS":
            return "|----";
        case "SUBCLASS":
            return "|------";
        case "GROUP":
            return "|--------";
        case "SUBGROUP":
            return "|----------";
    }
}

class Chart extends Component {
    constructor(props) {
        super(props)
        this.state = {
            width: props.width,
            height: props.height
        }
    }
    componentDidMount() {

        // Set the dimensions and margins of the diagram
        const margin = { top: 20, right: 30, bottom: 20, left: 90 },
            width = this.state.width - margin.left - margin.right,
            height = this.state.height - margin.top - margin.bottom;

        // append the svg object to the body of the page
        // appends a 'group' element to 'svg'
        // moves the 'group' element to the top left margin
        const svg = d3.select("body").append("svg")
            .attr("class", 'border')
            .attr("width", width + margin.right + margin.left)
            .attr("height", height + margin.top + margin.bottom)
            .attr("border", 1)
            .append("g")
            .attr("transform", "translate("
                + margin.left + "," + margin.top + ")");

        // add border path
        const bordercolor = '#8f8d8d';
        const border = 1;
        // const borderPath = svg.append("rect")
        //     // .attr("class", "border")
        //     .attr("x", -37)
        //     .attr("y", 30)
        //     .attr("width", width - margin.right - margin.left)
        //     .attr("height", height - margin.top - margin.bottom)
        //     .style("stroke", bordercolor)
        //     .style("fill", "none")
        //     .style("stroke-width", border);

        const descriptionDiv = d3.select("body")
            .append("div")
            .attr("id", "description");
        const tooltipDiv = d3.select("body")
            .append("div")
            .attr("class", "tooltip")
            .style("opacity", 0);

        var i = 0,
            duration = 750,
            root;

        // declares a tree layout and assigns the size
        const treemap = d3.tree().size([height, width]);

        // Assigns parent, children, height, depth
        root = d3.hierarchy(this.props.treeData, function (d) { return d.children; });
        // root = d3.hierarchy(treeTrueData, function (d) { return d.children; });
        root.x0 = height / 2;
        root.y0 = 0;

        // Collapse after the second level
        // root.children.forEach(collapse);

        update(root);

        // Collapse the node and all it's children
        function collapse(d) {
            if (d.children) {
                d._children = d.children
                d._children.forEach(collapse)
                d.children = null
            }
        }

        function showPrecedentNodesDescription(d) {
            var curr = d;
            var descriptions = [descriptionIndent(d) + curr.data.name];
            while (curr.parent != null) {
                curr = curr.parent;
                descriptions.splice(0, 0, descriptionIndent(curr) + curr.data.name);

            }
            descriptions.map(appendNodeDescription);
            console.log(`descriptions `)
            console.log(descriptions)
            console.log(`descriptionDiv ${descriptionDiv}`)
            console.log(descriptionDiv)
        }

        function appendNodeDescription(d) {
            descriptionDiv.append('div').attr('class', 'description')
                .text(d);
        }

        function removePrecedentNodesDescription() {
            document.getElementById("description").innerHTML = "";
            console.log("remove", document.getElementById("#description"));
        }

        function update(source) {

            // Assigns the x and y position for the nodes
            var treeMap = treemap(root);

            // Compute the new tree layout.
            var nodes = treeMap.descendants(),
                links = treeMap.descendants().slice(1);

            // Normalize for fixed-depth.
            nodes.forEach(function (d) { d.y = d.depth * 200 });

            // ****************** Nodes section ***************************

            // Update the nodes...
            var node = svg.selectAll('g.node')
                .data(nodes, function (d) { return d.id || (d.id = ++i); });

            // Enter any new modes at the parent's previous position.
            var nodeEnter = node.enter().append('g')
                .attr('class', 'node')
                .attr("transform", function (d) {
                    return "translate(" + source.y0 + "," + source.x0 + ")"
                        ;
                })
                .attr("text-anchor", d => d._children ? "end" : "start")
                .on('click', function (d) {
                    removePrecedentNodesDescription(d)
                    showPrecedentNodesDescription(d)
                })
            // .on('click', click);

            // Add Circle for the nodes
            nodeEnter.append('circle')
                .attr('class', 'node')
                .attr('class', function (d) {
                    return isFalseButPredicted(d) ? "node falsenode" : "node truenode";
                })
                .attr('r', 1e-6)
                .style("fill", function (d) {
                    return d._children ? d.data.true ? trueCircleColor : circleColor : "#fff";
                });

            // Add labels for the nodes
            nodeEnter.append('foreignObject')
                .attr("dy", ".35em")
                /*  .attr("x", function(d) {
                      // return d.children || d._children ? -13 : 13;
                      return -13;
                  })*/
                .attr("y", function (d) {
                    return -30;
                })
                .attr("text-anchor", function (d) {
                    return d.children || d._children ? "end" : "start";
                })
                .text(function (d) { return d.data.symbol; });

            var tooltip = d3.select("body").append("div")
                .attr("class", "tooltip") //用于css设置类样式
                .attr("opacity", 0.0);

            // Add tooltip
            // nodeEnter.on("mouseover", function (d) {
            //     // tooltipDiv.transition().duration(0).style("opacity", 0)
            //     // descriptionDiv.transition().duration(3000);
            //     showPrecedentNodesDescription(d);

            //     // tooltipDiv.transition().delay(1000).duration(200).style("opacity", .9)

            //     // tooltipDiv.html(d.data.name)
            //     //     .attr("id", "tooltip")
            //     //     .style("left", (d3.event.pageX) + "px")
            //     //     .style("top", (d3.event.pageY + 20) + "px")
            //     //     .style("opacity", 1.0);
            // })
            //     .on("mouseout", function (d) {
            //         removePrecedentNodesDescription();

            //         // tooltipDiv.style("opacity", 0.0);
            //         // tooltipDiv.transition().duration(200).style("opacity", .0)
            //         // d3.select("#tooltip").remove();
            //     });

            // UPDATE
            var nodeUpdate = nodeEnter.merge(node);

            // Transition to the proper position for the node
            nodeUpdate.transition()
                .duration(duration)
                .attr("transform", function (d) {
                    return "translate(" + d.y + "," + d.x + ")";
                });

            // Update the node attributes and style
            nodeUpdate.select('circle.node')
                .attr('r', 5)
                .style("fill", function (d) {
                    return d._children ? d.data.true ? trueCircleColor : circleColor : "#fff";
                })
                .attr('cursor', 'pointer');


            // Remove any exiting nodes
            var nodeExit = node.exit().transition()
                .duration(duration)
                .attr("transform", function (d) {
                    return "translate(" + source.y + "," + source.x + ")";
                })
                .remove();

            // On exit reduce the node circles size to 0
            nodeExit.select('circle')
                .attr('r', 1e-6);

            // On exit reduce the opacity of text labels
            nodeExit.select('foreignObject')
                .style('fill-opacity', 1e-6);

            // ****************** links section ***************************

            // Update the links...
            var link = svg.selectAll('path.link')
                .data(links, function (d) { return d.id; });

            // Enter any new links at the parent's previous position.
            var linkEnter = link.enter().insert('path', "g")
                // .attr("class", "link")
                .attr('class', function (d) {
                    // return isTrueNotPredicted(d) ? isFalseButPredicted(d) ? "link falselink" : "link truelink" : "link";
                    return isTrueAndPredicted(d) ? "link truelink" : isFalseButPredicted(d) ? "link falselink" : "link";
                })
                .attr('d', function (d) {
                    var o = { x: source.x0, y: source.y0 }
                    return diagonal(o, o)
                })
                .attr('stroke-width', function (d) {
                    return d.data.prob * 10;
                })
                .style('stroke-dasharray', function (d) {
                    return isTrueNotPredicted(d) ? ("3, 3") : ("0, 0");
                });

            // UPDATE
            var linkUpdate = linkEnter.merge(link);

            // Transition back to the parent element position
            linkUpdate.transition()
                .duration(duration)
                .attr('d', function (d) { return diagonal(d, d.parent) })
                .attr('stroke-width', function (d) {
                    return d.data.prob * 3;
                });

            // Remove any exiting links
            var linkExit = link.exit().transition()
                .duration(duration)
                .attr('d', function (d) {
                    var o = { x: source.x, y: source.y }
                    return diagonal(o, o)
                })
                .remove();


            // ****************** labels section ***************************
            // labelsDiv.text("asprijsdafjspoadifjpsadjfp")
            svg.append('circle')
                .attr("cx", 30)
                .attr("cy", 80)
                .attr("r", 6)
                .attr('class', 'node truenode')
                .style('stroke-width', 3)
                .style("fill", function (d) {
                    // return d._children ? d.data.true ? trueCircleColor : circleColor : "#fff";
                    return circleColor;
                });
            svg.append('text')
                .attr("x", 40)
                .attr('y', 85)
                .text("predicted true label")
                .classed("labels", true)

            svg.append('circle')
                .attr("cx", 30)
                .attr("cy", 100)
                .attr("r", 6)
                .attr('class', 'node falsenode')
                .style('stroke-width', 3)
                .style("fill", function (d) {
                    // return d._children ? d.data.true ? trueCircleColor : circleColor : "#fff";
                    return '#fff';
                });
            svg.append('text')
                .attr("x", 40)
                .attr('y', 105)
                .text("predicted false label")
                .classed("labels", true)

            svg.append('line')
                .attr("x1", 10)
                .attr("y1", 120)
                .attr("x2", 40)
                .attr("y2", 120)
                .attr('class', 'truelink')
                .style('stroke-dasharray', ('3, 3'))
            svg.append('text')
                .attr("x", 40)
                .attr('y', 125)
                .text("unpredicted true label")
                .classed("labels", true)
            // .attr("font-family", "Montserrat")
            // .attr("font-size", "14px")
            // .style("-webkit-text-stroke-width", "0.5px")


            // Store the old positions for transition.
            nodes.forEach(function (d) {
                d.x0 = d.x;
                d.y0 = d.y;
            });

            // Creates a curved (diagonal) path from parent to the child nodes
            function diagonal(s, d) {

                var path = `M ${s.y} ${s.x}
            C ${(s.y + d.y) / 2} ${s.x},
              ${(s.y + d.y) / 2} ${d.x},
              ${d.y} ${d.x}`

                return path
            }

            // Toggle children on click.
            function click(d) {
                if (d.children) {
                    d._children = d.children;
                    d.children = null;
                } else {
                    d.children = d._children;
                    d._children = null;
                }
                update(d);
            }
        }
    }

    render() {
        return (
            <div>
                <svg ref={node => this.node = node} width={this.state.width} height={this.state.height}></svg>
                {/* <selector>test</selector> */}
            </div>
        )
    }
}

export default Chart;