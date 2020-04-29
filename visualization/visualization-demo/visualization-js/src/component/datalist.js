import React, { Component } from "react";

class DataList extends Component {

    constructor(props) {
        super(props);
        this.state = {
            test: null
        };
    }

    render() {
        const { treeData, descLabels, leafNodesNum, descriptionDict } = this.props;
        const sliceLabels = descLabels.slice(0, leafNodesNum)
        console.log("datalist: type of treeData", typeof treeData)

        return (
            <div>
                {
                    sliceLabels.map((d, idx) => (
                        <div key={idx}>
                            <div className="list-label-name">
                                {d}:
                            </div>
                            <div className="list-label-content">
                                {eval(`descriptionDict.${d}`)}
                            </div>
                        </div>
                    ))
                }

            </div>
        )
    }
}

export default DataList;