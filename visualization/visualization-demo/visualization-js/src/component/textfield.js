import React, { Component } from "react";
import "./textfield.css"


class TextField extends Component {
    constructor(props) {
        super(props);
        this.state = {
            input: ""
        }

    }

    handleChange(event) {
        this.setState({
            input: event.target.value
        })
    }


    render() {
        console.log(this.state.input)
        return (
            <div>
                <label>
                    Input Document here:
                </label>
                <input type="text" className="documentInput" value={this.state.input} onChange={this.handleChange.bind(this)} />
                <button onClick={() => this.props.handleSubmit(this.state.input)} >
                    submit
                </button>
            </div>
        )
    }
}
export default TextField;

