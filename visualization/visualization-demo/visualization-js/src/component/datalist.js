import React, { Component } from "react";

class DataList extends Component {

    constructor(props) {
        super(props);
        this.state = {
            test: null
        };
    }

    render() {
        const { treeData, cpcCodes } = this.props;
        console.log("datalist: treeData", treeData)
        console.log("datalist: cpcCodes", cpcCodes)

        return (
            // <div className="options">
            //     {parts.map((part, index) => (
            //         <span key={index} style={{ fontWeight: part.highlight ? 700 : 400 }}>
            //             {part.text}
            //         </span>
            //     ))}
            // </div>
            <div>
                {treeData.map((d, idx) => (
                    <div>
                        {d.data.label}
                    </div>

                ))}
            </div>
        )
    }
}

export default DataList;