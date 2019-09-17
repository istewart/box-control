import React from 'react';

import {Form} from './Form.js';
import {Sessions} from './Sessions.js';
import './App.css';
import 'react-vis/dist/style.css';
import {XYPlot, LineSeries, XAxis, YAxis, HorizontalGridLines} from 'react-vis';

const colorsByColumn = {
  is_stim: "palevioletred",
  is_port_open: "green",
  is_licking: "orange",
};


const labelsByNumber = {
  .5: 'stim',
  2.5: 'lick',
  4.5: 'reward'
}


class App extends React.Component {
  state = {
    sessions: [],
    data: []
  };

  onAddSession = (session) => {
    //TODO: this does not seem like how one should add sessions?
    //idk tho
    this.setState({sessions: [...this.state.sessions, session]});
  };

  onReceiveData = (data) => {
    //roll over if over
    if (this.state.data.length==200){
      this.state.data.shift();
    }

    this.setState({
      data: [...this.state.data, data],
    });
  }

  render() {
    return (
      <div className="App">
        <header className="App-header">
          <Form 
            onAddSession={this.onAddSession}
            onReceiveData={this.onReceiveData}
          />
          <div className="graphs">
            <XYPlot height={300} width={400} >
              {['is_stim', 'is_licking', 'is_port_open'].map(
                (column, i) => (
                    <LineSeries
                      data={this.state.data.map(
                        (datum) => ({x: datum.timestamp, y: datum[column] + 2*i})
                      )}
                      color={colorsByColumn[column]}
                      fill={""}
                      curve="curveStep"
                    />
                )
              )}
              
              <HorizontalGridLines />
              <XAxis title="Time" />
              <YAxis title="" tickValues={[0.5,2.5,4.5]} tickFormat={v=>labelsByNumber[v]}/>
            </XYPlot>
          </div>
          <Sessions sessions={this.state.sessions} />
        </header>
      </div>
    );
  }
}

export default App;
