import React, { Component } from "react";
import Chart from "./tree";
import axios from "axios";
import { TextType } from "./TextType";


class TextField extends Component {
    constructor(props) {
        super(props);
        this.state = {
            type: this.props.type,
            treeData: null
        }

    }

    // handleSubmit = (value) => {
    //     // console.log("textfield value: ")
    //     // console.log(value)
    //     var url = `http://100.26.45.117:8000/demo/`

    //     axios.put(
    //         url,
    //         value,
    //         { headers: { "Content-Type": "text/plain" } }
    //     ).then((res) => {
    //         console.log("textfield return: ")
    //         console.log(res.data);
    //         this.setState({
    //             treeData: res.data,
    //         });
    //     })
    // }

    render() {
        const { type } = this.props
        return (
            <div>
                <label>
                    {type}
                </label>
                <input type="text" />
                <button onClick={() => this.props.handleSubmit("I want to test the result")} >
                    submit
                </button>
            </div>
        )
    }
}
export default TextField;

