import React from 'react';
import './App.css';

import openSocket from 'socket.io-client';


class App extends React.Component {
    state = {
      animalId: '',
      boxNumber: '',
      stage: 1,
      optogenetics: 'None',
      backgroundLuminensce: 32,
      sizeOne: 90,
      sizeTwo: 0,
      contrastLevels: [255],
      socket: openSocket(),
    }

    constructor(props) {
      super(props);
      
      this.state.socket.on('todo', () => {
        alert('event!');
      });
    }
    

    onChange = (name, value) => {
      this.setState({[name]: value});
    }

    onSubmit = (e) => {
      e.preventDefault();
      alert("todo");
    }

    render() {
      const {
        animalId,
        boxNumber,
        stage,
        optogenetics,
        backgroundLuminensce,
        sizeOne,
        sizeTwo,
        contrastLevels,
      } = this.state;

      return (
        <div className="App">
          <header className="App-header">
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
                name="stage"
                className="form-select"
                value={stage}
                onChange={(e) => this.onChange('stage', e.target.value)}
              >
                <option>None</option>
                <option>Activation</option>
                <option>Supression</option>
              </select>
              <select
                name="optogenetics"
                className="form-select"
                value={optogenetics}
                onChange={(e) => this.onChange('optogenetics', e.target.value)}
              >
                <option>1</option>
                <option>2</option>
                <option>3</option>
              </select>
              <input
                type="number"
                name="backgroundLuminensce"
                className="form-input"
                placeholder="todo"
                value={backgroundLuminensce}
                onChange={(e) => this.onChange('backgroundLuminensce', e.target.value)}
              />
              <input
                type="text"
                name="sizeOne"
                className="form-input"
                placeholder="todo"
                value={sizeOne}
                onChange={(e) => this.onChange('sizeOne', e.target.value)}
              />
              <input
                type="text"
                name="sizeTwo"
                className="form-input"
                placeholder="todo"
                value={sizeTwo}
                onChange={(e) => this.onChange('sizeTwo', e.target.value)}
              />
              <input
                type="text"
                name="contrastLevels"
                className="form-input"
                placeholder="todo"
                value={contrastLevels}
                onChange={(e) => this.onChange('contrastLevels', e.target.value)}
              />
              <button
                className="form-button"
                onClick={this.onSubmit}
              >
                Start Task
              </button>
            </form>
          </header>
        </div>
      );
    }
}

export default App;
