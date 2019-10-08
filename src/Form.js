import React from 'react';
import './App.css';

import openSocket from 'socket.io-client';

export class Form extends React.Component {
    state = {
      animalId: '',
      boxNumber: '',
      tier: 1,
      optogenetics: 'None',
      mW: 0,
      backgroundLuminensce: 128,
      sizeOne: 90,
      sizeTwo: 0,
      contrastLevels: [100],

      socket: new WebSocket('ws://0.0.0.0:8000/sockets/socket.io/'),
      dataPoints: [],
    };

    constructor(props) {
      super(props);

      this.state.socket.onmessage = (event) => {
        const msg = JSON.parse(event.data);

        if (msg.type === 'updateData') {
          //console.log(`Received Data: ${msg.data}`);
          this.props.onReceiveData(msg.data);
        } else if (msg.type === 'initTrial') {
          console.log(`New Trial: ${msg.data}`);
          this.props.onReceiveNewTrial(msg.data);
        } else if (msg.type === 'performanceUpdate'){
          console.log(`Performance Update: ${msg.data}`);
          this.props.onReceivePerformanceUpdate(msg.data);
        }else {
          console.log(msg);
        }
      }
    }

    onChange = (name, value) => {
      this.setState({[name]: value});
    };

  
    onSubmit = (e) => {
        e.preventDefault();

        const session = {
            animalId: this.state.animalId,
            boxNumber: this.state.boxNumber,
            tier: this.state.tier,
            optogenetics: this.state.optogenetics,
            backgroundLuminensce: this.state.backgroundLuminensce,
            mW: this.state.mW,
            sizeOne: this.state.sizeOne,
            sizeTwo: this.state.sizeTwo,
            contrastLevels: this.state.contrastLevels,
        };

        const message = {
          type: 'startSession',
          data: session,
        };
        
        this.state.socket.send(JSON.stringify(message));
        this.props.onAddSession(session);
    };

    onPause = (e) => {
      //don't submit the form
      e.preventDefault();
      this.state.socket.send(JSON.stringify({
        'type': 'pauseSession',
        'data': {'boxNumber': this.state.boxNumber}
      }));
    };
  
    render() {
      const {
        animalId,
        boxNumber,
        tier,
        optogenetics,
        mW,
        backgroundLuminensce,
        sizeOne,
        sizeTwo,
        contrastLevels,
      } = this.state;

      return (
            <form className="form">
              <input
                type="text"
                name="animalId"
                className="form-input"
                placeholder="Animal Id"
                value={animalId}
                onChange={(e) => this.onChange('animalId', e.target.value)}
              />
              <input
                type="text"
                name="boxNumber"
                className="form-input"
                placeholder="Box Number"
                value={boxNumber}
                onChange={(e) => this.onChange('boxNumber', e.target.value)}
              />
              
              <select
                name="tier"
                className="form-select"
                value={tier}
                onChange={(e) => this.onChange('tier', e.target.value)}
              >
                <option>1</option>
                <option>2</option>
                <option>3</option>
              </select>
              <select
                name="optogenetics"
                className="form-select"
                value={optogenetics}
                onChange={(e) => this.onChange('optogenetics', e.target.value)}
              >
                <option>None</option>
                <option>Activation</option>
                <option>Supression</option>
              </select>
              <input
                type="number"
                name="mW"
                className="form-input"
                placeholder="mW"
                value={mW}
                onChange={(e) => this.onChange('mW', e.target.value)}
              />
              <input
                type="number"
                name="backgroundLuminensce"
                className="form-input"
                placeholder="Background Luninensce"
                value={backgroundLuminensce}
                onChange={(e) => this.onChange('backgroundLuminensce', e.target.value)}
              />
              <input
                type="text"
                name="sizeOne"
                className="form-input"
                placeholder="Size One"
                value={sizeOne}
                onChange={(e) => this.onChange('sizeOne', e.target.value)}
              />
              <input
                type="text"
                name="sizeTwo"
                className="form-input"
                placeholder="Size Two"
                value={sizeTwo}
                onChange={(e) => this.onChange('sizeTwo', e.target.value)}
              />
              <input
                type="text"
                name="contrastLevels"
                className="form-input"
                placeholder="Contrast Levels (Comma Separated)"
                value={contrastLevels}
                onChange={(e) => this.onChange('contrastLevels', e.target.value)}
              />
              <button
                className="form-button"
                onClick={this.onSubmit}
              >
                Start Session
              </button>
              <button
                className="form-button"
                onClick={this.onPause}
              >
                Pause Session
              </button>
            </form>
      );
    }
}
