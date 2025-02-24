// import Message from './Message';

// function App() {
//   return <div><Message /></div>;
// }

// export default App;

import React, { useEffect, useState } from "react";
import axios from "axios";

function App() {
    const [entries, setEntries] = useState([]);

    useEffect(() => {
        axios.get("http://localhost:5000/entries")
            .then(response => setEntries(response.data))
            .catch(error => console.error("Error fetching data:", error));
    }, []);

    return (
        <div>
            <h1>MongoDB Entries</h1>
            <ul>
                {entries.map((entry, index) => (
                    <li key={index}>{entry.name} - {entry.subject}</li>
                ))}
            </ul>
        </div>
    );
}

export default App;
