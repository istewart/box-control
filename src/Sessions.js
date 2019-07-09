import React from 'react';

import './App.css';

export class Sessions extends React.Component {
    render() {
        return (
            <div className="sessions">
                {this.props.sessions.map((session) => (
                    <Session {...session} />
                ))}
            </div>
        );
    }
}

function Session({animalId}) {
    return (
        <div className="session" onClick={() => console.log('hi')}>
            <div>{animalId}</div>
        </div>
    );
}