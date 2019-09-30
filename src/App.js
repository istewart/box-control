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
    trial_number: 'NA',
    stim_size: 'Unknown',
    contrast: 'Unknown',
    trial_count: 'Unknown',
    hits: 'Unknown',
    false_alarms: 'Unknown',
    sessions: [],
    data: [],
  };

  onAddSession = (session) => {
    //TODO: this does not seem like how one should add sessions?
    //idk tho
    this.setState({sessions: [...this.state.sessions, session]});
  };

  onReceiveData = (data) => {
    //roll over if over
    if (this.state.data.length===200){
      this.state.data.shift();
    }

    this.setState({
      data: [...this.state.data, data],
    });
  }

  onReceiveNewTrial = ({trial_number, stim_size, contrast}) => {
    //map will make these variable names the values of these variables
    this.setState({
      trial_number,
      stim_size,
      contrast,
    })
  }

  onReceivePerformanceUpdate = ({total_count, hits, false_alarms}) => {
    this.setState({
      total_count,
      hits,
      false_alarms,
    })
  }

  render() {
    return (
      <div className="App">
        <header className="App-header">
          <Form 
            onAddSession={this.onAddSession}
            onReceiveData={this.onReceiveData}
            onReceiveNewTrial={this.onReceiveNewTrial}
            onReceivePerformanceUpdate={this.onReceivePerformanceUpdate}
          />
          <div className="center-panel">
            <div className = 'row'>
              <div classname = 'column'>
                <h4>Trial Number: {this.state.trial_number}</h4>
                <h4>Size: {this.state.stim_size}</h4>
                <h4>Contrast: {this.state.contrast}</h4>
              </div>
              <div classname = 'column'>
                <h4>Hit %: {this.state.hits}</h4>
                <h4>FA %: {this.state.false_alarms}</h4>
              </div>
            </div>
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
          </div>
          <Sessions sessions={this.state.sessions} />
        </header>
      </div>
    );
  }
}

export default App;
