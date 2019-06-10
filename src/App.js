import React from 'react';
import './App.css';

class App extends React.Component {
    state = {
      animal: '',
      box_number: '',
      stage: null,
      optogenetics: null,
      background_luminensce: 32,
      size_one: 90,
      size_two: null,
      contrast_levels: [255],
    }

    onChange = (name, value) => {
      this.setState({[name]: value});
    }

    onSubmit = () => {
      console.log("todo");
    }

    render() {
      return (
        <div className="App">
          <header className="App-header">
            <form className="form">
              <input
                type="text"
                name="animal"
                className="form-input"
                placeholder="Anima
                onChange={(e) => this.onChange('todo', e.target.value)}l Id"
              />
              <input
                type="text"
                name="box_number"
                className="form-input"
                placeholder="Box N
                onChange={(e) => this.onChange('todo', e.target.value)}umber"
              />
              <select
                name="stage"
                className="form-select"
              >
                <option>1</option>
                <option>2</option>
                <option>3</option>
              </select>
              <input
                type="text"
                name="animal"
                className="form-input"
                placeholder="todo"
                onChange={(e) => this.onChange('todo', e.target.value)}
              />
              <input
                type="text"
                name="animal"
                className="form-input"
                placeholder="todo"
                onChange={(e) => this.onChange('todo', e.target.value)}
              />
              <input
                type="text"
                name="animal"
                className="form-input"
                placeholder="todo"
                onChange={(e) => this.onChange('todo', e.target.value)}
              />
              <button onClick={this.onSubmit}>
                Start Task
              </button>
            </form>
          </header>
        </div>
      );
    }
}

export default App;
