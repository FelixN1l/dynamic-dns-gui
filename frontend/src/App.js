// frontend/src/App.js
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import DomainList from './components/DomainList';
import DomainForm from './components/DomainForm';

function App() {
    const [domains, setDomains] = useState([]);

    const fetchDomains = async() => {
        try {
            const response = await axios.get(`${process.env.REACT_APP_API_URL}/domains`);
            setDomains(response.data);
        } catch (error) {
            console.error('Error fetching domains:', error);
        }
    };

    useEffect(() => {
        fetchDomains();
    }, []);

    return ( <
        div style = {
            { padding: "20px" } } >
        <
        h1 > Dynamic DNS Health Monitor Dashboard < /h1> <
        DomainForm onDomainAdded = { fetchDomains }
        /> <
        DomainList domains = { domains }
        refreshDomains = { fetchDomains }
        /> <
        /div>
    );
}

export default App;