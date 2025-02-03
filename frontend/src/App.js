// frontend/src/App.js
import React, { useEffect, useState } from 'react';
import axios from 'axios';

function App() {
    const [domains, setDomains] = useState([]);
    const [newDomain, setNewDomain] = useState({ domain_name: '', zone_id: '', cf_api_token: '' });

    useEffect(() => {
        fetchDomains();
    }, []);

    const fetchDomains = async() => {
        try {
            const response = await axios.get(process.env.REACT_APP_API_URL + '/domains');
            setDomains(response.data);
        } catch (error) {
            console.error('Error fetching domains:', error);
        }
    };

    const addDomain = async(e) => {
        e.preventDefault();
        try {
            await axios.post(process.env.REACT_APP_API_URL + '/domains', newDomain);
            setNewDomain({ domain_name: '', zone_id: '', cf_api_token: '' });
            fetchDomains();
        } catch (error) {
            console.error('Error adding domain:', error);
        }
    };

    return ( <
        div style = {
            { padding: "20px" } } >
        <
        h1 > Dynamic DNS Health Monitor Dashboard < /h1> <
        h2 > Configured Domains < /h2> <
        ul > {
            domains.map((domain) => ( <
                li key = { domain.id } > { domain.domain_name }(Zone ID: { domain.zone_id }) < /li>
            ))
        } <
        /ul> <
        h2 > Add New Domain < /h2> <
        form onSubmit = { addDomain } >
        <
        div >
        <
        label > Domain Name: < /label> <
        input type = "text"
        value = { newDomain.domain_name }
        onChange = {
            (e) => setNewDomain({...newDomain, domain_name: e.target.value }) }
        required /
        >
        <
        /div> <
        div >
        <
        label > Zone ID: < /label> <
        input type = "text"
        value = { newDomain.zone_id }
        onChange = {
            (e) => setNewDomain({...newDomain, zone_id: e.target.value }) }
        required /
        >
        <
        /div> <
        div >
        <
        label > Cloudflare API Token: < /label> <
        input type = "password"
        value = { newDomain.cf_api_token }
        onChange = {
            (e) => setNewDomain({...newDomain, cf_api_token: e.target.value }) }
        required /
        >
        <
        /div> <
        button type = "submit" > Add Domain < /button> <
        /form> <
        /div>
    );
}

export default App;