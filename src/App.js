import React from 'react';

import {Form} from './Form.js';
import {Sessions} from './Sessions.js';
import './App.css';
import {XYPlot, LineMarkSeries, XAxis, YAxis, HorizontalGridLines} from 'react-vis';

const data = [
  {x: 0, y: 8},
  {x: 1, y: 5},
  {x: 2, y: 4},
  {x: 3, y: 9},
  {x: 4, y: 1},
  {x: 5, y: 7},
  {x: 6, y: 6},
  {x: 7, y: 3},
  {x: 8, y: 2},
  {x: 9, y: 0}
];

class App extends React.Component {
  state = {
    sessions: [],
  };

  onAddSession = (session) => {
    this.setState({sessions: [...this.state.sessions, session]});
  };

  render() {
    return (
      <div className="App">
        <header className="App-header">
          <Form onAddSession={this.onAddSession} />
          <div className="graphs">
            <XYPlot height={300} width={300} >
              <LineMarkSeries data={data} color="palevioletred" />
              <HorizontalGridLines />
              <XAxis title="X" />
              <YAxis title="Y" />
            </XYPlot>
          </div>
          <Sessions sessions={this.state.sessions} />
        </header>
      </div>
    );
  }
}

export default App;
