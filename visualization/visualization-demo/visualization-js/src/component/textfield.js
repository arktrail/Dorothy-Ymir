import React, { Component } from "react";
import Chart from "./tree";
import axios from "axios";
import TextType from "./TextType";

function submit(type, value) {
    console.log("textfield value: ")
    console.log(value)

    var url;
    if (type === TextType.DOCUMENT_ID) {
        url = `http://localhost:8000/demo/${value}`;
    } else if (type === TextType.PRIOR_ART) {
        url = `http://localhost:8000/demo/${value}`;
    }

    axios.get(url).then((res) => {
        console.log("textfield return: ")
        console.log(res.data);
        this.setState({
            treeData: res.data,
        });
    });
}

class TextField extends Component {
    constructor(props) {
        super(props);
        this.state = {
            type: this.props.type,
            treeData: null
        }

    }

    handleSubmit = (value) => {
        console.log("textfield value: ")
        console.log(value)

        var url;
        if (type === TextType.DOCUMENT_ID) {
            url = `http://localhost:8000/demo/${value}`;
        } else if (type === TextType.PRIOR_ART) {
            url = `http://localhost:8000/demo/${value}`;
        }

        axios.get(url, {}, {
            auth: {
                username: 'yyn1228',
                password: 'Dorothy2000'
            }
        }).then((res) => {
            console.log("textfield return: ")
            console.log(res.data);
            this.setState({
                treeData: res.data,
            });
        });

    }

    render() {
        const { type } = this.props
        return (
            <div>
                <label>
                    {type}
                </label>
                <input type="text" />
                <button onClick={} >
                    submit
                </button>
            </div>
        )
    }
}
export default TextField;

