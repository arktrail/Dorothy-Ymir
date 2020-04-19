import * as d3 from "d3";
import React, { Component } from "react";
import "./tree.css";
import { treePredictedData, treeLessData } from './data'

const PROB_LINK_MULTI = 1


// TTD:
// 2. add dot link lines for true-not-predicted node : x
// 3. add different color node for true-predicted node : x
// 1. add button to choose how many nodes I need to render
// 5. change the font size : x
// 6. add labels to

function descriptionClass(d) {
    switch (d.data.level) {
        case "SECTION":
            return "description-section";
        case "CLASS":
            return "description-class"
        case "SUBCLASS":
            return "description-subclass";
        case "GROUP":
            return "description-group";
        case "SUBGROUP":
            return "description-subgroup";
    }
}

class Tree extends Component {
    constructor(props) {
        super(props);
        this.state = {
            width: props.width,
            height: props.height,
            root: null,
            treemap: null,
        };
        this.isTrueNotPredicted = this.isTrueNotPredicted.bind(this);
        this.isFalseButPredicted = this.isFalseButPredicted.bind(this);
        this.isTrueAndPredicted = this.isTrueAndPredicted.bind(this);
        this.isPredicted = this.isPredicted.bind(this);
    }

    isTrueNotPredicted(d) {
        const {trueCodeSet} = this.props
        return trueCodeSet.has(d.data.symbol) && !this.isPredicted(d);
    }

    isFalseButPredicted(d) {
        const {trueCodeSet} = this.props
        return !trueCodeSet.has(d.data.symbol) && this.isPredicted(d);
    }

    isTrueAndPredicted(d) {
        const {trueCodeSet} = this.props
        return trueCodeSet.has(d.data.symbol) && this.isPredicted(d);
    }

    isPredicted(d) {
        return d.data.order < this.props.leafNodesNum;
    }

    componentDidMount() {
        const {width, height} = this.state
        const treeGraphPaddingLeft = 60

        // label container
        d3.select("#tree-graph")
            .append("svg")
            .attr("id", "labels")
            .attr("width", width)
            .attr("height", 80)

        // tree container
        d3.select("#tree-graph")
            .append("svg")
            .attr("id", "tree")
            .attr("width", width - treeGraphPaddingLeft)
            .attr("height", height)
            .attr("border", 1)
            .append("g")
            .attr("id", "nodes")
            .attr("transform", "translate(" + treeGraphPaddingLeft + ", 0)");

        d3.select("#tree-graph")
            .append("div")
            .attr("class", "tooltip")
            .style("opacity", 0);

        // description container 
        d3.select("#tree-graph")
            .append("div")
            .attr("id", "description")

        var root;

        // declares a tree layout and assigns the size
        const treemap = d3.tree().size([height, width]);

        // Assigns parent, children, height, depth
        root = d3.hierarchy(this.props.treeData, function (d) {
            return d.children;
        });
        // root = d3.hierarchy(treeTrueData, function (d) { return d.children; });
        root.x0 = height / 2;
        root.y0 = 0;

        // Collapse after the second level
        // root.children.forEach(collapse);

        this.drawLabels();

        this.update(root, root, treemap);
        this.copy(root);
        // console.log("root after copy", root);

        this.setState({
            root,
            treemap,
        });
    }

    componentDidUpdate() {
        this.filterNodeByLeafNodesNum(this.props.leafNodesNum, this.state.root);
    }

    drawLabel(label, circleClass, lineClass, x, y, dash) {
        const svg = d3.select("svg#labels");
        const line = svg
            .append("line")
            .attr("x1", x - 30)
            .attr("y1", y)
            .attr("x2", x - 5)
            .attr("y2", y)
            .attr("class", lineClass)
            .style("stroke-width", 1.5)
        if (dash) {
            line.style("stroke-dasharray", "3, 3");
        }
           
        svg
            .append("circle")
            .attr("cx", x)
            .attr("cy", y)
            .attr("r", 5)
            .attr("class", circleClass)
            .style("stroke-width", 3)
            .style("fill", "#fff");
        svg
            .append("text")
            .attr("x", x + 15)
            .attr("y", y + 5)
            .text(label)
            .classed("labels", true);
    }

    drawLabels() {
        const x = 30
        const y = 20
        this.drawLabel("predicted true label", "node truenode",  "truelink", x, y, false)
        this.drawLabel("unpredicted true label", "node truenode",  "truelink", x, y + 20, true)
        this.drawLabel("predicted false label", "node falsenode",  "falselink", x, y + 40, false)
    }

    filterNodeByLeafNodesNum(leafNodesNum, d) {
        const {trueCodeSet} = this.props
        if (!d || !d._children) return;
        var children = new Array();
        for (var i = 0; i < d._children.length; i++) {
            var child = d._children[i];
            if (child.data.order < leafNodesNum || trueCodeSet.has(child.data.symbol)) {
                children.push(child);
            }
        }
        d.children = children;
        d.children.forEach(this.filterNodeByLeafNodesNum.bind(this, leafNodesNum));
        this.update(d, this.state.root, this.state.treemap);
    }

    update(source, root, treemap) {
        const {trueCodeSet} = this.props

        var svg = d3.select("g#nodes");
        const duration = 750;
        var i = 0;

        // Assigns the x and y position for the nodes
        var treeMap = treemap(root);

        // Compute the new tree layout.
        var nodes = treeMap.descendants(),
            links = treeMap.descendants().slice(1);

        // Normalize for fixed-depth.
        nodes.forEach(function (d) {
            d.y = d.depth * 200;
        });

        // ****************** Nodes section ***************************

        // Update the nodes...
        var node = svg.selectAll("g.node").data(nodes, function (d) {
            return d.id || (d.id = ++i);
        });

        const this_ = this;
        // Enter any new modes at the parent's previous position.
        var nodeEnter = node
            .enter()
            .append("g")
            .attr("class", "node")
            .attr("transform", function (d) {
                return "translate(" + source.y0 + "," + source.x0 + ")";
            })
            // .attr("text-anchor", d => d._children ? "end" : "start")
            .on("click", function (d) {
                this_.removePrecedentNodesDescription(d);
                this_.showPrecedentNodesDescription(d);
            });
        // .on('click', click);

        // Add Circle for the nodes
        nodeEnter
            .append("circle")
            .attr("class", function (d) {
                return trueCodeSet.has(d.data.symbol) ? "node truenode" : "node falsenode"
            })
            .attr("r", 1e-6);

        // Add labels for the nodes
        nodeEnter
            .append("foreignObject")
            .attr("dy", ".35em")
            .attr("x", function (d) {
                return d.children ? 0 : 13;
            })
            .attr("y", function (d) {
                return d.children ? -30 : -10;
            })
            .attr("text-anchor", function (d) {
                return d.children || d._children ? "end" : "start";
            })
            .text(function (d) {
                return d.data.symbol;
            });

        var tooltip = d3
            .select("body")
            .append("div")
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
        nodeUpdate
            .transition()
            .duration(duration)
            .attr("transform", function (d) {
                return "translate(" + d.y + "," + d.x + ")";
            });

        // Update the node attributes and style
        nodeUpdate
            .select("circle.node")
            .attr("r", 5)
            .attr("class", function (d) {
                return trueCodeSet.has(d.data.symbol) ? "node truenode" : "node falsenode"
            })
            .attr("cursor", "pointer");

        // Remove any exiting nodes
        var nodeExit = node
            .exit()
            .transition()
            .duration(duration)
            .attr("transform", function (d) {
                return "translate(" + source.y + "," + source.x + ")";
            })
            .remove();

        // On exit reduce the node circles size to 0
        nodeExit.select("circle").attr("r", 1e-6);

        // On exit reduce the opacity of text labels
        nodeExit.select("foreignObject").style("fill-opacity", 1e-6);

        // ****************** links section ***************************

        // Update the links...
        var link = svg.selectAll("path.link").data(links, function (d) {
            return d.id;
        });

        // Enter any new links at the parent's previous position.
        var linkEnter = link
            .enter()
            .insert("path", "g")
            .attr("class", function (d) {
                return this_.isTrueAndPredicted(d)
                    ? "link truelink"
                    : this_.isFalseButPredicted(d)
                        ? "link falselink"
                        : "link";
            })
            .attr("d", function (d) {
                var o = { x: source.x0, y: source.y0 };
                return diagonal(o, o);
            })
            .attr("stroke-width", function (d) {
                return d.data.prob * PROB_LINK_MULTI;
            })
            .style("stroke-dasharray", function (d) {
                return this_.isTrueNotPredicted(d) ? "3, 3" : "0, 0";
            });

        // UPDATE
        var linkUpdate = linkEnter.merge(link);

        // Transition back to the parent element position
        linkUpdate
            .transition()
            .duration(duration)
            .attr("class", function (d) {
                return this_.isTrueAndPredicted(d)
                    ? "link truelink"
                    : this_.isFalseButPredicted(d)
                        ? "link falselink"
                        : "link";
            })
            .attr("d", function (d) {
                return diagonal(d, d.parent);
            })
            .attr("stroke-width", function (d) {
                return this_.isTrueNotPredicted(d) ? 1 : d.data.prob * PROB_LINK_MULTI;
            })
            .style("stroke-dasharray", function (d) {
                return this_.isTrueNotPredicted(d) ? "3, 3" : "0, 0";
            });

        // Remove any exiting links
        var linkExit = link
            .exit()
            .transition()
            .duration(duration)
            .attr("d", function (d) {
                var o = { x: source.x, y: source.y };
                return diagonal(o, o);
            })
            .remove();

        // ****************** labels section ***************************
        // labelsDiv.text("asprijsdafjspoadifjpsadjfp")
        
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
          ${d.y} ${d.x}`;

            return path;
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
            this.update(d);
        }
    }

    // Collapse the node and all it's children
    collapse(d) {
        if (d.children) {
            d._children = d.children;
            d._children.forEach(this.collapse);
            d.children = null;
        }
    }

    copy(d) {
        if (d.children) {
            d._children = d.children;
            d.children.forEach(this.copy.bind(this));
        }
    }

    showPrecedentNodesDescription(d) {
        let curr = d;
        let descriptions = [];
        if (d.data.name !== 'root') {
            descriptions.push(
                {
                    'className': descriptionClass(d),
                    'text': d.data.name
                }
            )
        }
        while (curr.parent !== null && curr.parent.data.name !== 'root') {
            curr = curr.parent;
            descriptions.splice(0, 0, 
                {
                    'className': descriptionClass(curr),
                    'text': curr.data.name
                }
            )
        }
        console.log("descriptions", descriptions)
        descriptions.map(this.appendNodeDescription)
    }

    appendNodeDescription(d) {
        console.log("className", d.className, "text", d.text)
        const descriptionDiv = d3.select("div#description");
        descriptionDiv.append("div").attr("class", "description" + ' ' + d.className).text(d.text);
    }

    removePrecedentNodesDescription() {
        document.getElementById("description").innerHTML = "";
    }

    render() {
        return <div></div>;
    }
}

export default Tree;

