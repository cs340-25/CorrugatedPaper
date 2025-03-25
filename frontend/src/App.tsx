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
            .then(response => {
                console.log(response.data); // Inspect the structure of the data
                setEntries(response.data);
            })
            .catch(error => console.error("Error fetching data:", error));
    }, []);

    return (
        <div>
            <h1>MongoDB Entries</h1>
            <ul>
                {entries.map((entry, index) => (
                    <li key={index}>
                        <b>{entry.subject} {entry.courseNumber} - {entry.courseTitle}</b>
                        <p>Description: {entry.courseDescription}</p>
                        <p>Avaliable sections:</p>
                        <ul>
                            {entry.classes.map((section, index) => (
                                <li>Instructor: {section.faculty.length == 0 ? "TBD" : section.faculty[0].displayName}<br/>
                                Meeting Times: {section.meetingsFaculty.length == 0 ? "00:00" : section.meetingsFaculty[0].meetingTime.beginTime} - {section.meetingsFaculty.length == 0 ? "00:00" : section.meetingsFaculty[0].meetingTime.endTime}
                                </li>
                            ))}
                        </ul>
                    </li>
                ))}
            </ul>
        </div>
    );
}

export default App;
