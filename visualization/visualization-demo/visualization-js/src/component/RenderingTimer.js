import React, {Component} from 'react'

const WAIT = {
    1: '.',
    2: '..',
    0: '...'
}

class RenderingTimer extends Component {
    constructor(props) {
        super(props);
        this.state = {
            time: 1,
        } 
        this._unmounted = false
    }

    componentDidMount() {
        this.timer = setInterval(
            () => this.tick(),
            300
        );
    }

    componentWillUnmount() {
        this._unmounted = true
        clearInterval(this.timer)
    }

    tick() {
        if (!this._unmounted) {
            this.setState(function (state) {
                return {
                    time: state.time + 1,
                };
            });
        }
    }

    render() {
        const {time} = this.state
        return (
            <div className="rendering">We are trying very hard to predict the cpc labels... Please be patient{WAIT[time % 3]}</div>
        );
    }
}

export default RenderingTimer


